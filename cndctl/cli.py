
def accept_continue(message):
    while True:
        choice = input("{}\n continue? [y/n] :".format(message)).lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False