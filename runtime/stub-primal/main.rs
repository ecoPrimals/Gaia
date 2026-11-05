fn main() {
    eprintln!("[stub] {} starting as placeholder primal", std::env::args().collect::<Vec<_>>().join(" "));
    loop { std::thread::sleep(std::time::Duration::from_secs(3600)); }
}
