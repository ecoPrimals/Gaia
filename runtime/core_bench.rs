// core_bench.rs - the measuring hand of core_profile.pi. Standard library only.
//   build: rustc --edition 2021 -O core_bench.rs
//   topo                          -> cores and caches as Windows reports them (which logical processors share which cache)
//   chase <cpu> <mb> <ms>         -> ns per random memory access over a working set of <mb> MB, pinned to one logical processor
//   bw    <cpu> <mb>              -> GB/s copied, one thread
//   scale <cpu,cpu,..> <ms> <mb>  -> one pinned thread per listed processor; <mb>=0 pure compute, else each chases its own <mb> MB
// Reads and measures only. The one thing it sets is the affinity of its own threads.
use std::hint::black_box;
use std::sync::{Arc, Barrier};
use std::time::{Duration, Instant};

#[link(name = "kernel32")]
extern "system" {
    fn GetCurrentThread() -> isize;
    fn SetThreadAffinityMask(thread: isize, mask: usize) -> usize;
    fn GetLogicalProcessorInformationEx(relationship: u32, buffer: *mut u8, len: *mut u32) -> i32;
}

fn pin(cpu: usize) {
    unsafe {
        SetThreadAffinityMask(GetCurrentThread(), 1usize << cpu);
    }
}

fn topo() {
    let mut len: u32 = 0;
    unsafe {
        GetLogicalProcessorInformationEx(0xffff, std::ptr::null_mut(), &mut len);
    }
    let mut buf = vec![0u8; len as usize];
    if unsafe { GetLogicalProcessorInformationEx(0xffff, buf.as_mut_ptr(), &mut len) } == 0 {
        println!("{{\"error\":\"topology unreadable\"}}");
        return;
    }
    let rd32 = |o: usize| u32::from_le_bytes(buf[o..o + 4].try_into().unwrap());
    let rd64 = |o: usize| u64::from_le_bytes(buf[o..o + 8].try_into().unwrap());
    let (mut off, mut cores, mut caches) = (0usize, vec![], vec![]);
    while off + 8 <= len as usize {
        let (rel, size) = (rd32(off), rd32(off + 4) as usize);
        if size == 0 {
            break;
        }
        match rel {
            // PROCESSOR_RELATIONSHIP: Flags +8, GroupMask +32
            0 => cores.push(format!("{{\"mask\":{},\"smt\":{}}}", rd64(off + 32), buf[off + 8] & 1)),
            // CACHE_RELATIONSHIP: Level +8, CacheSize +12, Type +16, GroupMask +40
            2 => caches.push(format!(
                "{{\"level\":{},\"kb\":{},\"type\":{},\"mask\":{}}}",
                buf[off + 8],
                rd32(off + 12) / 1024,
                rd32(off + 16),
                rd64(off + 40)
            )),
            _ => {}
        }
        off += size;
    }
    println!("{{\"cores\":[{}],\"caches\":[{}]}}", cores.join(","), caches.join(","));
}

// One random cycle through every slot (Sattolo), so each access lands somewhere unpredictable.
fn cycle(mb: usize, seed: u64) -> Vec<usize> {
    let n = mb * 1024 * 1024 / 8;
    let mut a: Vec<usize> = (0..n).collect();
    let mut s = seed | 1;
    for i in (1..n).rev() {
        s ^= s << 13;
        s ^= s >> 7;
        s ^= s << 17;
        a.swap(i, (s % i as u64) as usize);
    }
    a
}

fn chase_for(a: &[usize], dur: Duration) -> (u64, f64) {
    let (mut i, mut count, t) = (0usize, 0u64, Instant::now());
    loop {
        for _ in 0..200_000 {
            i = unsafe { *a.get_unchecked(i) };
        }
        count += 200_000;
        if t.elapsed() >= dur {
            break;
        }
    }
    black_box(i);
    (count, t.elapsed().as_secs_f64())
}

fn compute_for(dur: Duration, seed: u64) -> (u64, f64) {
    let (mut x, mut count, t) = (seed, 0u64, Instant::now());
    loop {
        for _ in 0..1_000_000 {
            x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            x ^= x >> 29;
        }
        count += 1_000_000;
        if t.elapsed() >= dur {
            break;
        }
    }
    black_box(x);
    (count, t.elapsed().as_secs_f64())
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let num = |i: usize| a.get(i).and_then(|s| s.parse::<usize>().ok()).unwrap_or(0);
    match a.get(1).map(|s| s.as_str()) {
        Some("topo") => topo(),
        Some("chase") => {
            pin(num(2));
            let set = cycle(num(3), 0x9E3779B97F4A7C15);
            let (count, secs) = chase_for(&set, Duration::from_millis(num(4) as u64));
            println!("{{\"mb\":{},\"ns_per_access\":{:.2}}}", num(3), secs * 1e9 / count as f64);
        }
        Some("bw") => {
            pin(num(2));
            let n = num(3) * 1024 * 1024;
            let src = vec![1u8; n];
            let mut dst = vec![0u8; n];
            let mut best = 0f64;
            for _ in 0..5 {
                let t = Instant::now();
                dst.copy_from_slice(&src);
                best = best.max(n as f64 / 1e9 / t.elapsed().as_secs_f64());
                black_box(dst[n / 2]);
            }
            println!("{{\"mb\":{},\"copy_gb_per_s\":{:.2}}}", num(3), best);
        }
        Some("scale") => {
            let cpus: Vec<usize> = a[2].split(',').filter_map(|s| s.parse().ok()).collect();
            let (dur, mb) = (Duration::from_millis(num(3) as u64), num(4));
            let gate = Arc::new(Barrier::new(cpus.len()));
            let hands: Vec<_> = cpus
                .iter()
                .map(|&cpu| {
                    let gate = gate.clone();
                    std::thread::spawn(move || {
                        pin(cpu);
                        let set = if mb > 0 { cycle(mb, 0x9E37 + cpu as u64 * 7919) } else { vec![] };
                        gate.wait();
                        if mb > 0 { chase_for(&set, dur) } else { compute_for(dur, cpu as u64 + 1) }
                    })
                })
                .collect();
            let per: Vec<f64> = hands.into_iter().map(|h| h.join().unwrap()).map(|(c, s)| c as f64 / s / 1e6).collect();
            println!(
                "{{\"threads\":{},\"mb_each\":{},\"total_mops\":{:.1},\"slowest_mops\":{:.1},\"fastest_mops\":{:.1}}}",
                per.len(),
                mb,
                per.iter().sum::<f64>(),
                per.iter().cloned().fold(f64::MAX, f64::min),
                per.iter().cloned().fold(0.0, f64::max)
            );
        }
        _ => eprintln!("usage: core_bench topo | chase <cpu> <mb> <ms> | bw <cpu> <mb> | scale <cpus> <ms> <mb>"),
    }
}
