import sqlite3
import re
from deepdiff import DeepDiff


def interface_shortener(interface_name):
    """shortens the long version of interface name

    Args:
        interface_name (str): takes full interface gigabithethernet1/0/1 line

    Returns:
        tupple: value1: shortened interface name, value2: interface numbers
    """    
    regex = re.compile(r"([A-Za-z]+)(\d+.*)")
    short_dict = {
    "gigabitethernet": "Gi",
    "tengigabitethernet": "Te",
    "tengige": "Te",
    "twentyfivegigabitethernet": "TF",
    "twentyfivegige": "TF",
    "fortygigabitethernet": "Fo",
    "fastethernet": "Fa",
    "port-channel": "Po",
    "loopback": "Lo",
    "hundredgige": "Hu",
    "ethernet": "Eth",
    "mgmteth": "Mg"
    }

    int_type, int_no = regex.search(interface_name.casefold()).groups()
    
    return (short_dict[int_type], int_no) if short_dict.get(int_type) else (int_type, int_no)


def make_int_dictionary(filename):
    '''gets the filename, returns int:config
    also makes a slot_dict global dictionary
    also makes int_no global int_no index to int_name dict
    '''
    regex = re.compile(r'\d+')
    int_no = {}
    slot_dict = {}
    int_dict = {}
    int_cfg = []
    unique_index = 0
    with open(filename) as f:
        for line in f:
            line = line.strip('\n')
            if "interface" in line and "/" in line:
                line = line.replace("interface", "")
                int_cfg = []
                int_name, no = interface_shortener(line)
                int_dict[int_name+no] = int_cfg
                int_no[unique_index] = int_name+no
                if a:=regex.findall(no):
                    slot_dict[unique_index] = [int_name] + [a[i] if i*-1 <= len(a) else 0 for i in range(-1, -4, -1)][::-1]
                else:
                    slot_dict[unique_index] = ('Ethernet', '0', '0', '0')
                unique_index += 1
                continue
            # if not line == '!' and line.startswith(' ') and not line.startswith(' des'):
            if not line == '!' and line.startswith(' '):
                # line = line.strip()
                int_cfg.append(line)
                continue
            if line.startswith('interface Vlan'): #here is the problem -- > where i detect end of interface configs
                break
        return int_dict, slot_dict, int_no


def load_ints(interfaces):
    """preparing the interfaces for db import

    function takes parsed interfaces dict, reads its 
    interface name, makes list of lists for db_import

    Args:
        interfaces (dict): dict of dict, value is dict

    Returns:
        list: db_info: list of lists
    """    
    regex = re.compile(r'\d+')
    db_info = []
    int_dict = {}
    unique_index = 0
    for interface in interfaces:
        int_name, no = interface_shortener(interface)
        int_dict[int_name+no] = interfaces[interface]
        if a:=regex.findall(no):
            db_info.append([unique_index, int_name+no, int_name] + [a[i] if i*-1 <= len(a) else 0 for i in range(-1, -4, -1)][::-1] + ["config"])
        else:
            db_info.append([unique_index, int_name+no, 'Ethernet', '0', '0', '0', "config"])
        unique_index += 1
    return int_dict, db_info


def create_lists_of_tupples(int_dict, slot_dict, int_no):
    """makes a slot flat raw data with int index

    take global int_no and int_dict (which contains configs)
    combines it with slot_dict and makes flat data for database

    Args:
        int_no (dict): int index to name dict
        int_dict (dict): int name to config dict
        slot_dict (dict): int type and slot info

    Returns:
        list: list of tupples which is slot data and config
    """    
    int_no_list = []
    for key in int_no:
        int_no_list.append((key, 
                        int_no[key],
                        slot_dict[key][0],
                        slot_dict[key][1],
                        slot_dict[key][2],
                        slot_dict[key][3],
                        '\n'.join(int_dict[int_no[key]])))
    
    return int_no_list
    

def uniquely_configured_int_groups(int_dict, structured=False):
    """groups the similar ints together


    Args:
        int_dict (dict): dict with key as interf. value as configs

    Returns:
        list: list of sets
    """    
    similarity_dict = {}
    for key in int_dict:    
        similar_int_set = set()
        for k in int_dict:
            if structured:
                if not DeepDiff(int_dict[k],
                        int_dict[key],
                        exclude_paths="root['status']"
                        ):
                    similar_int_set.add(k)
            else:                                 
                if int_dict[k] == int_dict[key]:
                    similar_int_set.add(k)
        if similar_int_set:   
            similarity_dict[key] = similar_int_set 

    # pprint(similarity_dict, sort_dicts=False)

    uniquely_config_ints = []
    for val in similarity_dict.values():    
        if val in uniquely_config_ints:        
            continue
        else:
            uniquely_config_ints.append(val)

    # pprint(uniquely_config_ints, sort_dicts=False)
    return uniquely_config_ints


def range_out_of_set(list):
    """Filters the single interfaces

    Filters the single interface sets, leaves out
    the ones with multiple elements and returns them
    as a list.

    Args:
        list (list): list of sets

    Returns:
        list: list of strings which is interface name
    """    
    same_config_ints = []
    for element in list:
        if len(element) > 1:
            same_config_ints.append(sorted(element))
    return same_config_ints


def write_to_db(int_no_list, conn):
    with conn:
        query = "DELETE from interfaces"
        conn.execute(query, )
        for rows in int_no_list:
            # print(rows)
            try:
                with conn:
                    query = "INSERT into interfaces values (?, ?, ?, ?, ?, ?, ?)"
                    conn.execute(query, rows)
            except sqlite3.IntegrityError as e:
                print("ID = {} exists".format(rows[0]))
                print('updating values')
                query = "REPLACE into interfaces values (?, ?, ?, ?, ?, ?, ?)"
                conn.execute(query, rows)


def cisco_range_packer(lst):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), 5):
        yield lst[i:i + 5]


def db_query_id(int_name, conn):
    with conn:
        values = (int_name, )
        conn.row_factory = sqlite3.Row
        query = "select * from interfaces where int_name=?"
        # print(query)
        result = conn.execute(query, values)
        return result.fetchone()[0]


def db_query(id, col, conn):
    with conn:
        conn.row_factory = sqlite3.Row
        query = "select * from interfaces where ID = '{}'".format(id)
        result = conn.execute(query)
        return result.fetchone()[col]


def create_db(conn):
    sql_query = '''create table interfaces (
    ID  int primary key,
    int_name    text,
    int_type    text,
    unit        int,
    slot        int,
    port        int,
    int_config  text
    );'''
    with conn:
        try:
            conn.executescript(sql_query)
        except:
            return "error"

if __name__ == "__main__":

    short_int = interface_shortener("TenGigE0/0/2/0")
    print(short_int)
