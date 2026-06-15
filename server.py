import socket
import os
import requests
from datetime import datetime
import fake_process  # <-- This links your mentor task to the trap

os.makedirs("xynera_logs", exist_ok=True)

def write_log(ip, session_time, message):
    filename = f"xynera_logs/attack_{ip}_{session_time}.log"
    with open(filename, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%H:%M:%S')} | {message}\n")

def run_honeypot():
    host = '0.0.0.0'
    port = 2222 
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    
    print(f"[*] Trap is set! Listening for attackers on port {port}...")
    
    try:
        while True:
            client, addr = server.accept()
            attacker_ip = addr[0]
            session_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            print(f"[!] Intrusion detected from {attacker_ip}")
            write_log(attacker_ip, session_time, "SESSION STARTED")
            
            fake_banner = "Welcome to Ubuntu 22.04.3 LTS\nubuntu@server:/home/ubuntu$ "
            client.send(fake_banner.encode('utf-8'))
            
            while True:
                try:
                    data = client.recv(1024)
                    if not data:
                        break
                    
                    command = data.decode('utf-8').strip()
                    if command:
                        print(f"[{attacker_ip}] typed: {command}")
                        write_log(attacker_ip, session_time, f"COMMAND EXECUTED: {command}")
                        
                        # --- THE INTERCEPTOR ---
                        if command == "ps":
                            # Pulls from your updated fake_process.py
                            fake_output = fake_process.ps() + "\n"
                            client.send(fake_output.encode('utf-8'))
                        else:
                            try:
                                ai_response = requests.post(
                                    "http://127.0.0.1:5000/generate", 
                                    json={"command": command}, 
                                    timeout=5
                                )
                                terminal_output = ai_response.json().get("output", "")
                            except Exception:
                                terminal_output = f"bash: {command}: command not found\n"
                            
                            client.send(terminal_output.encode('utf-8'))
                        # -----------------------
                        
                        client.send(b"ubuntu@server:/home/ubuntu$ ")
                except Exception:
                    break
                    
            print(f"[-] Attacker {attacker_ip} disconnected.")
            write_log(attacker_ip, session_time, "SESSION ENDED")
            client.close()
            
    except KeyboardInterrupt:
        print("\n[*] Shutting down the trap. Goodbye!")
        server.close()

if __name__ == "__main__":
    run_honeypot()
