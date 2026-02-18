# Pinned Kali for reproducibility (keep your digest if you already use one)
FROM kalilinux/kali-last-release@sha256:396fe3b46c76cf9fd095d9ccf630fc0bac9280f8118b8afb8be1df9e8c1e75ad

# Install headless + required tools
RUN apt-get update && \
    apt-get install -y \
      kali-linux-headless \
      nmap \
      curl \
      ca-certificates \
      iproute2 \
      sshpass && \
    rm -rf /var/lib/apt/lists/*

# Kali container nmap capability workaround (see Kali bug 9085)
RUN setcap cap_net_raw,cap_net_bind_service+eip /usr/lib/nmap/nmap

# Wrapper to avoid PyInstaller (_MEI) library-path pollution for child processes
RUN printf '%s\n' \
  '#!/bin/sh' \
  'unset LD_LIBRARY_PATH LD_LIBRARY_PATH_ORIG LD_PRELOAD' \
  'exec /usr/lib/nmap/nmap "$@"' \   
  > /usr/local/bin/nmap-native && chmod +x /usr/local/bin/nmap-native

#RUN printf '%s\n' \
#  '#!/bin/sh' \  # use the shell to run this scripts
#  'unset LD_LIBRARY_PATH LD_LIBRARY_PATH_ORIG LD_PRELOAD' \  # Remove env vars that PyInstaller sets so child apps don’t load wrong libs (avoids shared-lib conflicts) :contentReference[oaicite:0]{index=0}
#  'exec /usr/lib/nmap/nmap "$@"' \   # Run the real nmap binary with whatever args were passed in
#  > /usr/local/bin/nmap-native && \   # Write all that into a new script file at /usr/local/bin/nmap-native
#  chmod +x /usr/local/bin/nmap-native   # Make the script executable

WORKDIR /root/
CMD [ "sleep", "86400" ]
