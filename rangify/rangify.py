import helpers
import sqlite3
import os


def ranger(input):
    # create a db, pass it to needed files 
    

    with sqlite3.connect(":memory:") as conn:
        helpers.create_db(conn)
    if type(input) == str and os.path.isfile(input):
        int_dict, slot_dict, int_no = helpers.make_int_dictionary(input)
        helpers.write_to_db(helpers.create_lists_of_tupples(int_dict, slot_dict, int_no), conn)
        rangable_ints = helpers.range_out_of_set(helpers.uniquely_configured_int_groups(int_dict))
    elif type(input) == dict:
        int_dict, db_info = helpers.load_ints(input)
        helpers.write_to_db(db_info, conn)
        rangable_ints = helpers.range_out_of_set(helpers.uniquely_configured_int_groups(int_dict, structured=True))
        # pprint(rangable_ints)

    
    list_of_indexes = []
    for chuncks in rangable_ints:
        int_index_list = []
        for interfaces in chuncks:
            with conn:
                conn.row_factory = sqlite3.Row
                query = "select * from interfaces where int_name = '{}'".format(interfaces)
                result = conn.execute(query)
                int_index_list.append(result.fetchone()[0])
        list_of_indexes.append(sorted(int_index_list))


    main_sep_list = []
    ardicil_groups = []
    separated_list = []
    for chunk in sorted(list_of_indexes):
        for int_index in chunk:
            if int_index == chunk[0]:
                ardicil_groups = []
                ardicil_groups.append(int_index)
                prev = int_index
                continue
            if (int_index == prev + 1 and 
                helpers.db_query(int_index, 5, conn) == helpers.db_query(prev, 5, conn) + 1 and
                helpers.db_query(int_index, 4, conn) == helpers.db_query(prev, 4, conn) and
                helpers.db_query(int_index, 2, conn) == helpers.db_query(prev, 2, conn) and
                helpers.db_query(int_index, 3, conn) == helpers.db_query(prev, 3, conn)):
                ardicil_groups.append(int_index)
                prev = int_index
                continue
            else:
                separated_list.append(ardicil_groups)
                ardicil_groups = []
                ardicil_groups.append(int_index)
                prev = int_index
        else:
            separated_list.append(ardicil_groups)
            ardicil_groups = []
        separated_list.sort()
        main_sep_list.append(separated_list)
        separated_list = []

    # print(main_sep_list)

    
    whole_rangable_int = sum(sum(main_sep_list, []), [])

    # ToDo extract repeating pattern for both input types to function 
    # or do it using decorator
    if type(input) == str and os.path.isfile(input):
        for key in int_no:
            if key not in whole_rangable_int:
                print('interface ' + helpers.db_query(key, 1, conn))
                print(helpers.db_query(key, 6, conn))
        for chunk in main_sep_list:
            # in this chunk interface configs are the same
            for range_div in helpers.cisco_range_packer(chunk):
                range_pack = []
                for sub_chunk in range_div:
                    if len(sub_chunk) > 1:
                        max = len(sub_chunk) - 1
                        range_pack.append(
                            (helpers.db_query(sub_chunk[0], 1, conn) + '-' + str(helpers.db_query(sub_chunk[max], 5, conn))))
                    else:
                        range_pack.append((helpers.db_query(sub_chunk[0], 1, conn)))
                if len(range_pack) == 1 and "-" not in range_pack[0]:
                    print('interface ', end='')
                    print(", ".join(range_pack))
                    print(helpers.db_query(chunk[0][0], 6, conn))
                else:
                    print('interface range ', end='')
                    print(", ".join(range_pack))
                    print(helpers.db_query(chunk[0][0], 6, conn))
    elif type(input) == dict:
        result = {}
        for key in int_dict:
            if helpers.db_query_id(key, conn) not in whole_rangable_int:
                result[key] = int_dict[key]
        for chunk in main_sep_list:
            # in this chunk interface configs are the same
            for range_div in helpers.cisco_range_packer(chunk):
                range_pack = []
                for sub_chunk in range_div:
                    # print(sub_chunk)
                    if len(sub_chunk) > 1:
                        max = len(sub_chunk) - 1
                        range_pack.append((helpers.db_query(sub_chunk[0], 1, conn) + '-' + str(helpers.db_query(sub_chunk[max], 5, conn))))
                    else:
                        range_pack.append((helpers.db_query(sub_chunk[0], 1, conn)))
                if len(range_pack) == 1 and "-" not in range_pack[0]:
                    result[", ".join(range_pack)] = int_dict[helpers.db_query(chunk[0][0], 1, conn)]
                else:
                    result["range " + ", ".join(range_pack)] = int_dict[helpers.db_query(chunk[0][0], 1, conn)]
        return result

if __name__ == "__main__":
    #Todo: make a package, make range_it as main, others as helpers
    #Todo: test with large quantity of data, empty str, emtpry, structure, wrong int name etc...
    #Todo: check if sqlmemory will be working fine in case of flask multiaccess
    #Todo: convert to OOP

    sample_ints = {
        "GigabitEthernet0/1": {},
        "GigabitEthernet0/2": {},
        "GigabitEthernet0/4": {},
        "GigabitEthernet0/3": {},
        "GigabitEthernet1/0/1": {},
        "GigabitEthernet1/0/2": {},
        "GigabitEthernet1/0/4": {},
        "GigabitEthernet3/4/2": {},
        "GigabitEthernet3/4/3": {},
        "GigabitEthernet3/5/3": {},
        "GigabitEthernet3/6/3": {},
        "GigabitEthernet4/0/3": {},
        "GigabitEthernet4/1/3": {},
        "GigabitEthernet4/2/3": {},
        "GigabitEthernet2/0/4": {},
        "GigabitEthernet3/1/4": {},
        "GigabitEthernet3/1/5": {}
    }


    config_file = os.path.join(os.path.dirname(__file__), 'test_config.ios')
    # ranger(config_file)
    print(ranger(sample_ints))