from difflib import SequenceMatcher 


class EditTreeNode(object):
    def __init__(self, val):
        self.left = None
        self.right = None
        self.val = val

    def apply(self, word):
        assert isinstance(word, str)
        if isinstance(self.val[0], str):  # replace
            if word == self.val[0]:
                return self.val[1]
            else:
                return -1
        elif isinstance(self.val[0], int):  # split
            assert isinstance(self.left, EditTreeNode)
            assert isinstance(self.right, EditTreeNode)
            word_left = word[:self.val[0]]
            word_mid = word[self.val[0]: len(word)-self.val[1]]
            word_right = word[len(word)-self.val[1]:]

            word_left = self.left.apply(word_left)
            word_right = self.right.apply(word_right)

            if word_left == -1 or word_right == -1:
                return -1

            return word_left + word_mid + word_right

    def __str__(self):
        if self.left is None:  # leaf
            return str(self.val)
        else:
            left_str = str(self.left)
            right_str = str(self.right)
            ret = str(self.val) + '\n'
            for line in left_str.split('\n'):
                ret += '  ' + line + '\n'
            for line in right_str.split('\n'):
                ret += '  ' + line + '\n'
            return ret.strip()

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        if not isinstance(other, EditTreeNode):
            return False
        else:
            if (self.left == other.left) and (self.right == other.right) and (self.val == other.val):
                return True
            return False


def longestSubstring(str1,str2): 
    seqMatch = SequenceMatcher(None,str1,str2) 
    match = seqMatch.find_longest_match(0, len(str1), 0, len(str2)) 
    return (match.a, match.b, match.size)


def editTree(str1, str2):
    if str1 is None or str2 is None: return None
    idx1, idx2, size = longestSubstring(str1, str2)
    if size == 0:
        return EditTreeNode((str1, str2))
    node = EditTreeNode((idx1, len(str1) - idx1 - size))
    node.left = editTree(str1[:idx1], str2[:idx2])
    node.right = editTree(str1[idx1 + size:], str2[idx2 + size:])
    return node
