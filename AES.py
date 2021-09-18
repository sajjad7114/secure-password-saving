class AES:
    def __init__(self):
        self.block_size = int(128/8)
        self.rounds = 10
#                       0    1    2    3    4    5    6    7    8    9    A    B    C    D    E    F
        self.s_box = [[ 99, 124, 119, 123, 242, 107, 111, 197,  48,   1, 103,  43, 254, 215, 171, 118],
                      [202, 130, 201, 125, 250,  89,  71, 240, 173, 212, 162, 175, 156, 164, 114, 192],
                      [183, 253, 147,  38,  54,  63, 247, 204,  52, 165, 229, 241, 113, 216,  49,  21],
                      [  4, 199,  35, 195,  24, 150,   5, 154,   7,  18, 128, 226, 235,  39, 178, 117],
                      [  9, 131,  44,  26,  27, 110,  90, 160,  82,  59, 214, 179,  41, 227,  47, 132],
                      [ 83, 209,   0, 237,  32, 252, 177,  91, 106, 203, 190,  57,  74,  76,  88, 207],
                      [208, 239, 170, 251,  67,  77,  51, 133,  69, 249,   2, 127,  80,  60, 159, 168],
                      [ 81, 163,  64, 143, 146, 157,  56, 245, 188, 182, 218,  33,  16, 255, 243, 210],
                      [205,  12,  19, 236,  95, 151,  68,  23, 196, 167, 126,  61, 100,  93,  25, 115],
                      [ 96, 129,  79, 220,  34,  42, 144, 136,  70, 238, 184,  20, 222,  94,  11, 219],
                      [224,  50,  58,  10,  73,   6,  36,  92, 194, 211, 172,  98, 145, 149, 228, 121],
                      [231, 200,  55, 109, 141, 213,  78, 169, 108,  86, 244, 234, 101, 122, 174,   8],
                      [186, 120,  37,  46,  28, 166, 180, 198, 232, 221, 116,  31,  75, 189, 139, 138],
                      [112,  62, 181, 102,  72,   3, 246,  14,  97,  53,  87, 185, 134, 193,  29, 158],
                      [225, 248, 152,  17, 105, 217, 142, 148, 155,  30, 135, 233, 206,  85,  40, 223],
                      [140, 161, 137,  13, 191, 230,  66, 104,  65, 153,  45,  15, 176,  84, 187,  22]]

        self.matrix = [[2, 3, 1, 1],
                       [1, 2, 3, 1],
                       [1, 1, 2, 3],
                       [3, 1, 1, 2]]

        self.inverse_matrix = [[14, 11, 13, 9],
                               [9, 14, 11, 13],
                               [13, 9, 14, 11],
                               [11, 13, 9, 14]]

    def mult(self, num1, num2):
        result = 0
        for i in range(7, -1, -1):
            if num1 >= 2**i:
                num = num2 * 2**i
                if num >= 256:
                    n = int(num/256)
                    j = 0
                    while n > 0:
                        if n % 2 == 1:
                            num -= 256*(2**j)
                            num = 27*(2**j) ^ num
                            j = 0
                            n = int(num/256)
                        else:
                            n = int(n/2)
                            j += 1
                num1 -= 2**i
                result = num ^ result
        return result

    def add_round_key(self, block_matrix, key_matrix, index):
        for i in range(len(block_matrix)):
            for j in range(len(block_matrix[0])):
                a = block_matrix[i][j]
                b = key_matrix[i][index*4+j]
                block_matrix[i][j] = a ^ b

    def sub_bytes(self, block_matrix):
        for i in range(len(block_matrix)):
            for j in range(len(block_matrix[0])):
                row = int(block_matrix[i][j] / 16)
                column = block_matrix[i][j] % 16
                block_matrix[i][j] = self.s_box[row][column]

    def inverse_sub_bytes(self, block_matrix):
        for i in range(len(block_matrix)):
            for j in range(len(block_matrix[0])):
                row = -1
                column = -1
                for ii in range(len(self.s_box)):
                    if row != -1 and column != -1:
                        break
                    for jj in range(len(self.s_box[0])):
                        if self.s_box[ii][jj] == block_matrix[i][j]:
                            row = ii
                            column = jj
                            break
                block_matrix[i][j] = row * 16 + column

    def shift_rows(self, block_matrix):
        for i in range(len(block_matrix)):
            for k in range(i):
                element = block_matrix[i].pop(0)
                block_matrix[i].append(element)

    def inverse_shift_rows(self, block_matrix):
        for i in range(len(block_matrix)):
            for k in range(4-i):
                element = block_matrix[i].pop(0)
                block_matrix[i].append(element)

    def mix_columns(self, block_matrix):
        result = [[], [], [], []]
        for i in range(len(block_matrix)):
            for j in range(len(block_matrix[0])):
                num = 0
                for k in range(len(self.matrix)):
                    num = num ^ self.mult(self.matrix[i][k], block_matrix[k][j])
                result[i].append(num)
        return result

    def inverse_mix_columns(self, block_matrix):
        result = [[], [], [], []]
        for i in range(len(block_matrix)):
            for j in range(len(block_matrix[0])):
                num = 0
                for k in range(len(self.inverse_matrix)):
                    num = num ^ self.mult(self.inverse_matrix[i][k], block_matrix[k][j])
                result[i].append(num)
        return result

    def key_expansion(self, key_matrix):
        for i in range(4, 44):
            if i % 4 != 0:
                for j in range(4):
                    key_matrix[j].append(key_matrix[j][i-1] ^ key_matrix[j][i-4])
            else:
                temp = [key_matrix[1][i-1], key_matrix[2][i-1], key_matrix[3][i-1], key_matrix[0][i-1]]
                for j in range(4):
                    row = int(temp[j] / 16)
                    column = temp[j] % 16
                    temp[j] = self.s_box[row][column]
                    if j == 0:
                        rc = 2**(int(i/4-1))
                        while rc >= 256:
                            rc -= (256-27)
                        temp[j] = temp[j] ^ rc
                    key_matrix[j].append(temp[j] ^ key_matrix[j][i-4])

    def encrypt_block(self, block, key):
        block_matrix = [[], [], [], []]
        key_matrix = [[], [], [], []]
        for i in range(len(block)):
            block_matrix[i % 4].append(block[i])
            key_matrix[i % 4].append(key[i])

        # key expansion
        self.key_expansion(key_matrix)

        # Round 0
        self.add_round_key(block_matrix, key_matrix, 0)

        # Round 1 to N-1
        for i in range(1, self.rounds):
            self.sub_bytes(block_matrix)
            self.shift_rows(block_matrix)
            block_matrix = self.mix_columns(block_matrix)
            self.add_round_key(block_matrix, key_matrix, i)

        # Round N
        self.sub_bytes(block_matrix)
        self.shift_rows(block_matrix)
        self.add_round_key(block_matrix, key_matrix, self.rounds)

        result = []
        for i in range(len(block_matrix)):
            for j in range(len(block_matrix[0])):
                result.append(block_matrix[j][i])

        return result

    def decrypt_block(self, block, key):
        block_matrix = [[], [], [], []]
        key_matrix = [[], [], [], []]
        for i in range(len(block)):
            block_matrix[i % 4].append(block[i])
            key_matrix[i % 4].append(key[i])

        # key expansion
        self.key_expansion(key_matrix)

        # Round N
        self.add_round_key(block_matrix, key_matrix, self.rounds)

        # Round N-1 to 1
        for i in range(self.rounds-1, 0, -1):
            self.inverse_shift_rows(block_matrix)
            self.inverse_sub_bytes(block_matrix)
            self.add_round_key(block_matrix, key_matrix, i)
            block_matrix = self.inverse_mix_columns(block_matrix)

        # Round 0
        self.inverse_shift_rows(block_matrix)
        self.inverse_sub_bytes(block_matrix)
        self.add_round_key(block_matrix, key_matrix, 0)

        result = []
        for i in range(len(block_matrix)):
            for j in range(len(block_matrix[0])):
                result.append(block_matrix[j][i])

        return result

    def word2vec(self, word):
        vec = [ord(i) for i in word]
        return vec

    def vec2word(self, vec):
        word = ''.join(chr(i) for i in vec)
        return word

    def vec2hex(self, vec):
        heximal = ''.join(hex(i)[2:].zfill(2) for i in vec)
        return heximal

    def hex2vec(self, heximal):
        vec = [int(heximal[2*i], 16) * 16 + int(heximal[2*i+1], 16) for i in range(int(len(heximal)/2))]
        return vec

    def encrypt(self, input_word, key_word):
        input_vector = self.word2vec(input_word)
        key = self.word2vec(key_word)
        output_vector = []
        for i in range(int(len(input_vector) / self.block_size)):
            block = input_vector[i*self.block_size: (i+1)*self.block_size]
            result = self.encrypt_block(block, key)
            for element in result:
                output_vector.append(element)
        output_hex = self.vec2hex(output_vector)
        return output_hex

    def decrypt(self, input_hex, key_word):
        input_vector = self.hex2vec(input_hex)
        key = self.word2vec(key_word)
        output_vector = []
        for i in range(int(len(input_vector) / self.block_size)):
            block = input_vector[i*self.block_size: (i+1)*self.block_size]
            result = self.decrypt_block(block, key)
            for element in result:
                output_vector.append(element)
        output_word = self.vec2word(output_vector)
        return output_word


# text = "sajjadsalari7114sajjadsalari7115"
# key = "hello09876543210"
# aes = AES()
# cipher = aes.encrypt(text, key)
# print(cipher)
# plain = aes.decrypt(cipher, key)
# print(plain)
