from jsonrpcserver import Methods

methods = Methods()
@methods.add
def ping():
    return 'pong'

if __name__ == '__main__':
    methods.serve_forever()
