from icmp import ping
import argparse 


if __name__ == "__main__":
    

    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    parser.add_argument('--n_packets', type=int, default=3)
    args = parser.parse_args()

    ping(args.host)