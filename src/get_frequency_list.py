import argparse


def get_frequency_list(language):


def _parse_arguments()
    """ parse the arguments from the commandline

    Arguments:
        None
    Returns:
        Namespace
    """
    argparse.ArgumentParser(description='Get the word frequencies for a language')
    parser.add_argument('--language', dest=language, required=True
            help='the language we want the list for')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_arguments()
    frequency_list = get_frequency_list(args.language)
    print('\n'.join(frequency_list)
