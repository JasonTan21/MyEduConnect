FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server default-mysql-client curl sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -s /bin/bash student \
    && echo "student:student123" | chpasswd \
    && echo "root:toor" | chpasswd \
    && mkdir -p /run/sshd /app/uploads /var/backups/myeduconnect \
    && printf '#!/bin/bash\nset -e\nmkdir -p /var/backups/myeduconnect\ntar -czf /var/backups/myeduconnect/app-backup.tgz /app >/dev/null 2>&1 || true\necho "Backup completed: /var/backups/myeduconnect/app-backup.tgz"\n' > /usr/local/bin/myedu-backup \
    && chown student:student /usr/local/bin/myedu-backup \
    && chmod 775 /usr/local/bin/myedu-backup \
    && echo "student ALL=(root) NOPASSWD: /usr/local/bin/myedu-backup" > /etc/sudoers.d/myedu-backup \
    && chmod 440 /etc/sudoers.d/myedu-backup \
    && chmod 777 /app/uploads \
    && chmod 777 /var/backups/myeduconnect \
    && echo "PermitRootLogin yes" >> /etc/ssh/sshd_config \
    && echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config

COPY . .

EXPOSE 8080 22
CMD service ssh start && python app.py
