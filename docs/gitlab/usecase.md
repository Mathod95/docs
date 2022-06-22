    .. note::
        Pour activer l'utilisation du protocole mTLS sur le service XXX du namespace XXX, déclarez le cotenue suivant:

    .. code-block::

        wget https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-generic-amd64.raw

        virt-customize -a debian-11-generic-amd64.raw --install qemu-guest-agent

        DATE=$(date +"%Y%m%d")
        qm create 1000 --name "DEBIAN11-$DATE" --memory 8192 --balloon 4096 --net0 virtio,bridge=vmbr0 --cores 2 --sockets 4
        qm importdisk 1000 debian-11-generic-amd64.raw local-zfs
        qm set 1000 --scsihw virtio-scsi-pci --scsi0 local-zfs:vm-1000-disk-0
        qm set 1000 --serial0 socket
        qm set 1000 --boot c --bootdisk scsi0
        qm set 1000 --tablet 0
        qm set 1000 --ostype l26
        qm set 1000 --agent 1,fstrim_cloned_disks=1
        qm set 1000 --scsi1 local-zfs:cloudinit
        qm resize 1000 scsi0 +48G
        qm template 1000
                
        qm clone 1000 110 --name DEBIAN11 --storage local-zfs --full --target SRV01
        qm set 110 --ipconfig0 ip=146.59.254.96/32,gw=152.228.224.254
        qm set 110 --net0 virtio,bridge=vmbr0,macaddr=02:00:00:23:da:6b
        qm set 110 --ciuser mathod
        qm set 110 --cipassword mathod
