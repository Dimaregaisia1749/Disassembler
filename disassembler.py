import pandas as pd

def find_command(hex):
    byte = int(hex, 16)
    for i in range(len(codes)):
        mask = and_masks[i]
        res = bin(byte&mask)
        if res == codes[i]:
            print(codes[i])
    

def get_df(path='codes.csv'):   
    df = pd.read_csv(path)
    and_masks = list(map(int, df['Mask and'].to_list()))
    xor_masks = list(map(int, df['Mask xor'].to_list()))
    codes = int, df['command'].to_list()
    return df, codes, and_masks, xor_masks

df, codes, and_masks, xor_masks = get_df()
print(and_masks)
with open('hex.txt') as file:
    for line in file:
        line = line.strip()
        NN = int(line[1:3], 16)
        AA = int(line[3:7], 16)
        CC = int(line[7:9], 16)

        if NN:
            DD = line[9:9+NN*2]
        quartets = [DD[i: i+4] for i in range(0, NN*2, 4)]
        print(line, DD, quartets)
        print(NN, AA, CC)

        reversed_bytes = []
        for quartet in quartets:
            reversed_bytes.append(quartet[2: 4] + quartet[0: 2])
        print(reversed_bytes)

        merged = []
        for i in range(1, len(reversed_bytes)):
            quartet = reversed_bytes[i]
            last_quart = reversed_bytes[i-1]
            print(quartet, last_quart)
            if quartet[:2] == '94':
                continue
            if last_quart[:2] == '94':
                merged.append(last_quart+quartet)
            else:
                merged.append(quartet)

        assembly = [] 
        for command in merged:
            assembly.append(find_command(command))