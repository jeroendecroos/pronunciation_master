import commandline
import database
import resources
import data_generators


def _store_data(args):
    db_engine = database.create_engine(args.db_config)
    if args.which_table == 'create_empty':
        database.init_database(db_engine, resources.db_structure)
    else:
        table = database.Table.from_database(args.which_table, db_engine)
        row_generator = data_generators.RowGenerators.get(
            args.which_table,
            args,
            )
        table.add_data(row_generator(args.language), row_generator.buffer_size)


if __name__ == '__main__':
    description = 'Store different produced data in a database'
    options = data_generators.RowGenerators.get_all_options()
    args = commandline.LanguageAndDatabaseOutput.parse_arguments(
        description,
        options, 
        )
    _store_data(args)
