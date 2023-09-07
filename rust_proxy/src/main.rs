use std::net::{TcpListener, TcpStream};
use std::thread;
use std::io::{Read, Write};

fn main() {
    let listener = TcpListener::bind("127.0.0.1:8080").expect("Failed to bind to address");

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                thread::spawn(|| {
                    handle_client(stream);
                });
            }
            Err(e) => {
                eprintln!("Error accepting connection: {}", e);
            }
        }
    }
}

fn handle_client(mut stream: TcpStream) {
    let mut buffer = [0; 1024];
    let mut request = String::new();

    if let Err(_) = stream.read(&mut buffer) {
        return;
    }

    // Convert the buffer to a string
    request.push_str(&String::from_utf8_lossy(&buffer));

    // Check if the request contains a password field
    if request.contains("password=") {
        // Log the password attempt
        let password_attempt = request
            .lines()
            .find(|line| line.contains("password="))
            .unwrap_or("");

        println!("Password Attempt: {}", password_attempt);
    }

    // Forward the request to the Flask server
    let mut flask_stream = TcpStream::connect("127.0.0.1:5000").expect("Failed to connect to Flask server");

    if let Err(_) = flask_stream.write(request.as_bytes()) {
        return;
    }

    let mut flask_response = String::new();
    if let Err(_) = flask_stream.read_to_string(&mut flask_response) {
        return;
    }

    if let Err(_) = stream.write(flask_response.as_bytes()) {
        return;
    }
}
