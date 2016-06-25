"""Unit test for the _trie module."""
from flake8.plugins import _trie as trie


class TestTrie(object):
    """Collection of tests for the Trie class."""

    def test_traverse_without_data(self):
        """Verify the behaviour when traversing an empty Trie."""
        tree = trie.Trie()
        assert list(tree.traverse()) == []

    def test_traverse_with_data(self):
        """Verify that traversal of our Trie is depth-first and pre-order."""
        tree = trie.Trie()
        tree.add('A', 'A')
        tree.add('a', 'a')
        tree.add('AB', 'B')
        tree.add('Ab', 'b')
        tree.add('AbC', 'C')
        tree.add('Abc', 'c')
        # The trie tree here should look something like
        #
        #      <root>
        #     /      \
        #    A        a
        #  /  |
        # B   b
        #    / \
        #   C   c
        #
        # And the traversal should look like:
        #
        # A B b C c a
        expected_order = ['A', 'B', 'b', 'C', 'c', 'a']
        for expected, actual_node in zip(expected_order, tree.traverse()):
            assert actual_node.prefix == expected

    def test_find(self):
        """Exercise the Trie.find method."""
        tree = trie.Trie()
        tree.add('A', 'A')
        tree.add('a', 'a')
        tree.add('AB', 'AB')
        tree.add('Ab', 'Ab')
        tree.add('AbC', 'AbC')
        tree.add('Abc', 'Abc')

        assert tree.find('AB').data == ['AB']
        assert tree.find('AbC').data == ['AbC']
        assert tree.find('A').data == ['A']
        assert tree.find('X') is None


class TestTrieNode(object):
    """Collection of tests for the TrieNode class."""

    def test_add_child(self):
        """Verify we add children appropriately."""
        node = trie.TrieNode('E', 'E is for Eat')
        assert node.find_prefix('a') is None
        added = node.add_child('a', 'a is for Apple')
        assert node.find_prefix('a') is added

    def test_add_child_overrides_previous_child(self):
        """Verify adding a child will replace the previous child."""
        node = trie.TrieNode('E', 'E is for Eat', children={
            'a': trie.TrieNode('a', 'a is for Apple')
        })
        previous = node.find_prefix('a')
        assert previous is not None

        added = node.add_child('a', 'a is for Ascertain')
        assert node.find_prefix('a') is added

    def test_find_prefix(self):
        """Verify we can find a child with the specified prefix."""
        node = trie.TrieNode('E', 'E is for Eat', children={
            'a': trie.TrieNode('a', 'a is for Apple')
        })
        child = node.find_prefix('a')
        assert child is not None
        assert child.prefix == 'a'
        assert child.data == 'a is for Apple'

    def test_find_prefix_returns_None_when_no_children_have_the_prefix(self):
        """Verify we receive None from find_prefix for missing children."""
        node = trie.TrieNode('E', 'E is for Eat', children={
            'a': trie.TrieNode('a', 'a is for Apple')
        })
        assert node.find_prefix('b') is None

    def test_traverse_does_nothing_when_a_node_has_no_children(self):
        """Verify traversing a node with no children does nothing."""
        node = trie.TrieNode('E', 'E is for Eat')
        assert list(node.traverse()) == []

    def test_traverse(self):
        """Verify traversal is depth-first and pre-order."""
        root = trie.TrieNode(None, None)
        node = root.add_child('A', 'A')
        root.add_child('a', 'a')
        node.add_child('B', 'B')
        node = node.add_child('b', 'b')
        node.add_child('C', 'C')
        node.add_child('c', 'c')
        # The sub-tree here should look something like
        #
        #      <root>
        #     /      \
        #    A        a
        #  /  |
        # B   b
        #    / \
        #   C   c
        #
        # And the traversal should look like:
        #
        # A B b C c a
        expected_order = ['A', 'B', 'b', 'C', 'c', 'a']
        for expected, actual_node in zip(expected_order, root.traverse()):
            assert actual_node.prefix == expected
