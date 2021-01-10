from __syntax_extensions__ import pep634

def is_diagonal(p):
    match p:
        case (x, y) if x == y:
            return True
        case (_, _):
            return False

print(is_diagonal((0, 0)))
print(is_diagonal((0, 1)))
print(is_diagonal((1, 0)))
print(is_diagonal((1, 1)))
print(is_diagonal(0))
