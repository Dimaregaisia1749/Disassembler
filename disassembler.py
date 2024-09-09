import pandas as pd

def find_command(hex_code, starting_byte):
    byte = int(hex_code, 16)
    possible = []
    for i in range(len(codes)):
        command = commands[i]
        and_mask = int(and_masks[i], 2)
        xor_mask = int(xor_masks[i], 2)
        ans = (byte&and_mask)^xor_mask
        if ans == 0:
            params = get_params(command, ((4 - (len(bin(byte)[2:]) % 4))%4)*'0' + bin(byte)[2:], codes[i].replace(' ', ''), offset[i])
            possible.append((command, params))

    command, params = possible[0][0], possible[0][1]
    clear_params = []

    bytes = []
    curr = ''
    for i in hex_code:
        curr += i
        if len(curr) == 4:
            bytes.append(curr)
            curr = ''

    reversed_bytes = []
    for quartet in bytes:
        reversed_bytes.append(quartet[2: 4] + ' ' + quartet[0: 2])

    if command == 'nop':
        res = f"{hex(starting_byte)[2:]}:\t{' '.join(reversed_bytes).lower()}\t\t{command}\n"
        return res
    
    for symb, param in params.items():
        if symb in ('d', 'r'):
            clear_params.append('r' + str(int(param, 16)))
        elif command.split()[0] in ('rjmp', 'breq', 'bren', 'brbs') and symb == 'k':
            clear_params.append('.' + param[0] + str(abs(int(param, 16))))
        else:
            clear_params.append(param)

    params = []
    for param in clear_params:
        if param[0] == 'r' or len(param) == 4 or command.split()[0] == 'rjmp':
            params.append(param)
        else:
            params.append(param[:2] + '0' + param[2])
    if len(reversed_bytes) == 1:
        tabs = '\t\t'
    else:
        tabs = '\t'
    res = f"{hex(starting_byte)[2:]}:\t{' '.join(reversed_bytes).lower()}{tabs}{command.split()[0].replace('*', '')}\t{', '.join(params)}\n"
    return res

def get_params(command, byte, mnemonica, offset):
    possible_params = {'Rd': 'd', 'Rr': 'r', 'Rdl': 'd', 'K': 'K', 'k': 'k', 'P': 'P', 's': 's', 'b': 'b'}
    if len(command.split()) == 1:
        return
    symbs_of_params = [possible_params[i] for i in command.split()[1].split(',')]
    res_params = {}
    for symb in symbs_of_params:
        value_of_param = ''
        for i in range(len(mnemonica)):
            if mnemonica[i] == symb:
                value_of_param += byte[i]

        sign = ''
        if command.split()[0].replace('*', '') in ('rjmp', 'breq', 'bren', 'brbs') and symb == 'k':
            if value_of_param[0] == '1':
                value_of_param = int(value_of_param.replace('1', '_').replace('0', '1').replace('_', '0'), 2)
                value_of_param = bin(value_of_param+1)
                sign = '-'
            else:
                sign = '+'
        
        if command.split()[0].replace('*', '') in ('ldi', 'subi', 'sbci'):
            if symb in ('d', 'r'):
                value_of_param = bin(int(value_of_param, 2)+16)

        if offset and symb == 'k':  
            value_of_param = hex(int(value_of_param, 2) << 1)
        else:
            value_of_param = hex(int(value_of_param, 2))

        res_params[symb] = sign+value_of_param
    return res_params


def get_df(path='codes.csv'):   
    df = pd.read_csv(path)
    masks = df['Mask'].to_list()
    and_masks = df['Mask and'].to_list()
    xor_masks = df['Mask xor'].to_list()
    codes = df['Code'].to_list()
    commands = df['command'].to_list()
    offset = list(map(int, df['offset'].to_list()))
    return df, commands, codes, masks, and_masks, xor_masks, offset

def check_control_sum(seq):
    sm = 0
    for i in range(len(seq)//2):
        b = seq[i*2:i*2+2]
        sm += int(b, 16)
    if(sm%256) != 0:
        raise ValueError('Control sum not valid!')

df, commands, codes, masks, and_masks, xor_masks, offset = get_df()


with open('hex.txt') as file:
    assembly = [] 
    starting_byte = 0
    for line in file:
        line = line.strip()
        NN = int(line[1:3], 16)
        check_control_sum(line[1:])
        if NN:
            DD = line[9:9+NN*2]
        quartets = [DD[i: i+4] for i in range(0, NN*2, 4)]

        reversed_bytes = []
        for quartet in quartets:
            reversed_bytes.append(quartet[2: 4] + quartet[0: 2])

        merged = []
        last_quart = ''
        for i in reversed_bytes:
            quartet = i
            if last_quart:
                merged.append(last_quart+quartet)
                last_quart = ''
            elif quartet[:3] == '940': 
                last_quart = i
            else:
                merged.append(quartet)
        
        for command in merged:
            assembly.append(find_command(command, starting_byte))
            starting_byte += len(command)//2
    
    with open('output.txt', 'w') as output:
        output.writelines(assembly)