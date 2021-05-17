import re
import sre_yield
import csv
import string
import argparse

def get_line(file) :
    string = ''
    for c in file :
        if (c == '\n') :
            return string
        string += c

def get_ith_line(file, index) :
    for i, c in enumerate(file) :
        if (c == '\n') :
            index -= 1
            continue
        if (index == 0) :
            return get_line(file[i:])
    return -1

#Checks that the regEx word matches the characters
def try_word(word, regEx) :
    for i, letter in enumerate(word[1]) :
        if (letter != '.' and letter != regEx[i]) :
            return False
    return True

#Filters out the words produced by the regEx and have different length
def filter_list(regExList, length) :
    lst = []
    for w in regExList :
        if (len(w) == length and w not in lst) :
            lst.append(w)
    return lst

#Checks if the crossword is completed!
def all_full(words):
    for i in range(len(words)):
        if (words[i][0]) :
            return False
    return True

def make_copy(words) :
    copy = {}
    for i in range(len(words)) :
        copy[i] = words[i]
    return copy

#Gives a score for each word(to filled) that depends of how many letters are already there
def complete_ratio(word) :
    count = 0
    for letter in word[1] :
        if (letter != '.') :
            count += 1
    return count/len(word)

def choose_most_complete(words, visited) :
    best = -0.1
    index = -1 
    for i in range(len(words)) :
        if (words[i][0] and i not in visited) :
            ratio = complete_ratio(words[i])
            if (best < ratio) :
                index = i
                best = ratio
    return index

def solve_cross(words, regExs, used) :
    if (all_full(words)) :
        return words

    visited = {-1}
    i = choose_most_complete(words, visited)
    if (i == -1) :
        return False
    visited.add(i)
    regEx = get_ith_line(regExs, 0)
    reg_i = 0
    while regEx != -1 : 
        if (reg_i in used) :
            reg_i += 1
            regEx = get_ith_line(regExs, reg_i)
            continue
        used.add(reg_i)
        regExList = sre_yield.AllStrings(regEx, charset=string.ascii_uppercase, max_count=5)
        regExList = filter_list(regExList, len(words[i][1]))
        for w in regExList:
            w = list(w)
            if (try_word(words[i], w)) :
                w0 = words[i][0]
                w1 = words[i][1]
                w2 = words[i][2]
                words[i] = [False, w, w2]
                words = update(words, words[i], i)
                if (is_valid(words)) :
                    copy = make_copy(words)
                    sol = solve_cross(copy, regExs, used)
                    if (sol):
                        return sol
                    else :
                        words[i] = [w0, w1, w2]
                        words = update(words, words[i], i)
                        continue
        reg_i += 1
        regEx = get_ith_line(regExs, reg_i)
        used.remove(reg_i-1)

    return False

def is_valid(words) :
    for i in range(len(words)):
        for word in words[i][2] :
            where = words[i][2][word]
            letter_pos = words[word][2][i]
            letter = words[i][1][letter_pos]
            if (letter != words[word][1][where]) :
                if (letter != '.' and words[word][1][where] != '.'):
                    return False
    return True 

def update(words, word, index) :
    for w in word[2] :
        where = word[2][w]
        letter_pos = words[w][2][index]
        letter = word[1][letter_pos]
        words[w][1][where] = letter
    return words

def update_word_info(words) :
    for i in range(len(words)):
        for word in words[i][2] :
            where = words[i][2][word]
            letter_pos = words[word][2][i]
            letter = words[i][1][letter_pos]
            if (letter != '.' and words[word][1][where] == '.'):
                words[word][1][where] = letter 
    return words


def init_word_info(line) :
    counter = 0
    string = ''
    word_id = 0
    word_letters = ''
    common_letters = {}
    which = 0
    where = 0 
    empty = False 
    for c in line :
        if (c == '.') :
            empty = True

        if (c == ',' and counter == 0) :
            word_id = int(string)
            counter += 1
            string = ''
        elif (c == ',' and counter == 1) :
            word_letters = list(string)
            counter += 1
            string = ''
        elif (c == ',' and (counter % 2 == 1)) :
            where = int(string)
            counter += 1
            string = ''
            common_letters[which] = where
        elif (c == ',' and (counter % 2 == 0)) :
            which = int(string)
            counter += 1
            string = ''
        else :
            string += c

    where = int(string)
    common_letters[which] = where
    return (empty, word_id, word_letters, common_letters)


def find_regEx(word, regExs) :
    regEx = get_ith_line(regExs, 0)
    reg_i = 0
    while regEx != -1 : 
        regExList = sre_yield.AllStrings(regEx, charset=string.ascii_uppercase, max_count=5)
        for w in regExList :
            if (list(w) == word):
                return regEx
        reg_i += 1
        regEx = get_ith_line(regExs, reg_i)
    

def print_solution(words, regExs) :
    for i in range(0, len(words)) :
        word = ''
        regEx = find_regEx(words[i][1], regExs)
        for c in words[i][1] :
            word += c
        print(i, regEx, word)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('crossFile')
    parser.add_argument('regExFile')
    args = parser.parse_args()

    csvFile = open(args.crossFile, newline='')
    crossword = csv.reader(csvFile, delimiter=' ')

    words = {} 
    regExUsed = {}
    for line in crossword:
        if (line != []) :
            word = (init_word_info(line[0]))
            words[word[1]] = [word[0], word[2], word[3]]


    regExFile = open(args.regExFile, newline='')
    regExs = regExFile.read()

    words = update_word_info(words)
    solution = solve_cross(words, regExs, {-1})
    if (solution[0][1]) :
        print_solution(solution, regExs)
    else :
        print("No solution!")

    csvFile.close()
    regExFile.close()

if __name__ == "__main__":
    main()
