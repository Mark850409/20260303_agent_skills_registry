import bcrypt
import os

password = b'admin'
# Generate salt and hash it
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

# Write to auth/htpasswd
htpasswd_line = f"admin:{hashed.decode('utf-8')}\n"

with open('auth/htpasswd', 'w', encoding='utf-8', newline='\n') as f:
    f.write(htpasswd_line)

print("Generated htpasswd with bcrypt format.")
