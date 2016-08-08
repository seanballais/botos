FROM ubuntu:16.04

# Update the OS first
RUN apt-get update
RUN apt-get install -y python3-dev python3-pip sqlite3 libsqlite3-dev

# Add the necessary files
ADD requirements.txt /src/requirements.txt
RUN cd /src; pip3 install -r requirements.txt

# Bundle app source
ADD . /src

# Expose a port for using through a LAN connection.
EXPOSE 8080

# Execute the commands.
CMD ["python3", "/src/app.py"]


