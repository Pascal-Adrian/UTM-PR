import argparse

from raft import RaftNode, NodeState


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='RAFT Node Driver')

    parser.add_argument(
        '-p',
        '--port',
        type=int,
        help='Port for the node (e.g., 1) resulting in 300n, where n is the port number'
    )

    parser.add_argument(
        '-pp',
        '--peer-ports',
        type=int,
        nargs='+',
        help='Ports for the nodes in the cluster (e.g., 3000 3001 3002)'
    )

    parser.add_argument(
        '-m',
        '--manager-port',
        type=int,
        help='Port for the manager (e.g., 8000)'
    )

    args = parser.parse_args()
    print('Port:', args.port)
    print('Peer Ports:', args.peer_ports)

    node = RaftNode('127.0.0.1', args.port, args.manager_port, args.peer_ports)

    node.run()


if __name__ == "__main__":
    main()