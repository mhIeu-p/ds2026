#!/usr/bin/env python3
# mpi_transfer.py
#
# Usage (example):
#   mpirun -np 2 python3 mpi_transfer.py <FILE_TO_SEND> [-o OUTPUT_DIR]
#
# Rank 1: sender (reads the file and sends it)
# Rank 0: receiver (receives the file and writes it to disk)

from mpi4py import MPI
import os
import sys
import argparse

CHUNK_SIZE = 4096

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def send_file(file_path, dest_rank=0):
    """Send a file from this rank to the destination rank."""
    if not os.path.isfile(file_path):
        if rank == 1:
            print(f"[-] File not found: {file_path}")
        MPI.Abort(comm, 1)

    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)

    # Encode filename into bytes
    name_bytes = filename.encode("utf-8")

    if rank == 1:
        print(f"[Rank {rank}] Sending file '{filename}' ({filesize} bytes) to rank {dest_rank}.")

    # 1) Send filename length (int) + filename (bytes)
    comm.send(len(name_bytes), dest=dest_rank, tag=1)
    comm.send(name_bytes, dest=dest_rank, tag=2)

    # 2) Send file size
    comm.send(filesize, dest=dest_rank, tag=3)

    # 3) Send file content in chunks
    sent = 0
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break

            # Send the chunk
            comm.send(chunk, dest=dest_rank, tag=4)
            sent += len(chunk)

            # Progress indicator
            if rank == 1:
                print(f"\r[Rank {rank}] Sent {sent}/{filesize} bytes", end="", flush=True)

    # Send empty chunk to signal end of file
    comm.send(b"", dest=dest_rank, tag=4)

    if rank == 1:
        print("\n[Rank 1] File sent successfully.")


def recv_file(src_rank=1, out_dir="."):
    """Receive a file from source rank and write it to output directory."""
    os.makedirs(out_dir, exist_ok=True)

    # 1) Receive filename
    name_len = comm.recv(source=src_rank, tag=1)
    name_bytes = comm.recv(source=src_rank, tag=2)
    filename = name_bytes.decode("utf-8", errors="replace")
    safe_name = os.path.basename(filename)

    # 2) Receive file size
    filesize = comm.recv(source=src_rank, tag=3)

    out_path = os.path.join(out_dir, "received_" + safe_name)
    print(f"[Rank 0] Receiving file '{filename}' ({filesize} bytes)")
    print(f"[Rank 0] Saving as: {out_path}")

    # 3) Receive chunks and write to file
    received = 0
    with open(out_path, "wb") as f:
        while True:
            chunk = comm.recv(source=src_rank, tag=4)

            # End-of-file marker
            if len(chunk) == 0:
                break

            f.write(chunk)
            received += len(chunk)
            print(f"\r[Rank 0] Received {received}/{filesize} bytes", end="", flush=True)

    print("\n[Rank 0] File transfer complete.")


def main():
    parser = argparse.ArgumentParser(description="MPI file transfer (rank 1 -> rank 0)")
    parser.add_argument("file", nargs="?", help="Path to file to send (used by rank 1)")
    parser.add_argument("--out", "-o", default=".", help="Output directory for received file (rank 0)")
    args = parser.parse_args()

    # Need at least 2 ranks
    if size < 2:
        if rank == 0:
            print("[-] Need at least 2 MPI processes (rank 0 receiver, rank 1 sender).")
        MPI.Finalize()
        sys.exit(1)

    if rank == 0:
        # Receiver role
        recv_file(src_rank=1, out_dir=args.out)

    elif rank == 1:
        # Sender role
        if not args.file:
            print("[-] Rank 1: you must specify the file to send.")
            MPI.Abort(comm, 1)
        send_file(args.file, dest_rank=0)

    else:
        # Other ranks not used in this simple implementation
        print(f"[Rank {rank}] Idle (unused rank).")

    MPI.Finalize()


if __name__ == "__main__":
    main()
