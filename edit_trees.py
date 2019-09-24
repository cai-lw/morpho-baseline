from difflib import SequenceMatcher 

class Node(object):
    def __init__(self, val):
        self.left = None
        self.right = None
        self.val = val
    

def longestSubstring(str1,str2): 
     seqMatch = SequenceMatcher(None,str1,str2) 
     match = seqMatch.find_longest_match(0, len(str1), 0, len(str2)) 
     return (match.a, match.b, match.size)
    

def editTree(str1, str2):
    if str1 is None or str2 is None: return None
    idx1, idx2, size = longestSubstring(str1, str2)
    if size == 0:
        return Node((str1, str2))
    node = Node((idx1, len(str1) - idx1 - size))
    node.left = editTree(str1[:idx1], str2[:idx2])
    node.right = editTree(str1[idx1 + size:], str2[idx2 + size:])
    return node
    
def test(root):
    if root is not None:
        print(root.val)
        test(root.left)     
        test(root.right)     

if __name__ == '__main__':
    root = editTree("najtrudniejszy", "trudny")
    test(root)


