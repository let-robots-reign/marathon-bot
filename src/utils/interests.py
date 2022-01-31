def get_interests_list():
    with open('../interests.txt', 'r', encoding='utf8') as infile:
        return [line.strip() for line in infile.readlines()]
