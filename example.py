from flake8 import _trie as trie


tree = trie.Trie()
for i in range(5):
    tree.add('E103', 'E103-listener-{0}'.format(i))
    j = i + 1
    tree.add('E1{0}3'.format(j), 'E1{0}3-listener'.format(j))
for i in range(10):
    tree.add('W1{0:02d}'.format(i), 'W1{0:02d}-listener'.format(i))
