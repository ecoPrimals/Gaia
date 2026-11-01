/**
 * caertel-life - Skeletal Module
 * Supports structural integrity and life-sustaining processes through interconnected biological systems.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = 3000;

function getFeedData(feed) {
    return new Promise((resolve, reject) => {
        http.get(`http://localhost:${feed}/data`, (res) => {
            let data = '';
            res.on('data', (chunk) => {
                data += chunk;
            });
            res.on('end', () => {
                resolve(data);
            });
        }).on('error', (err) => {
            reject(err);
        });
    });
}

async function processFeeds() {
    try {
        const digestiveData = await getFeedData(3001);
        const respiratoryData = await getFeedData(3002);
        console.log('Digestive Data:', digestiveData);
        console.log('Respiratory Data:', respiratoryData);
    } catch (error) {
        console.error('Error processing feeds:', error);
    }
}

async function startServer() {
    const server = http.createServer(async (req, res) => {
        if (req.url === '/status') {
            res.writeHead(200, { 'Content-Type': 'text/plain' });
            res.end('Server is running');
        } else {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('Not Found');
        }
    });

    server.listen(PORT, () => {
        console.log(`caertel-life server running at http://localhost:${PORT}/`);
        setInterval(processFeeds, 5000);
    });

    server.on('error', (err) => {
        console.error('Server error:', err);
    });
}

startServer();
