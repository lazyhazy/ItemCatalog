# Item Catalog Demo

This project helps to create Item Catalog where user can view all the Catalog and their items. Registered user can create new Catalog Item, edit and delete any item.


## Prerequisites

### Install Linux VM

* Setup a Linux virtual Machine using vagrant. Instructions for which can be found [here](https://github.com/udacity/fullstack-nanodegree-vm)
* Once the setup is successfully completed, bring up the virtual machine with command `vagrant up`
* Then log into it using the command `vagrant ssh`


### Extract the ZIP:
  * Extract the attached _catalog.zip_ and `cd` into extracted folder _catalog_


# Run Command
Now, run the following command to create a database:
```
python database_setup.py
```

# Fill up Data in database_setup
Run the following command to prepopulate some initial data into database_setup
```
python lotofcatalog.py
```


# Run ItemCatalog Application
Finally, to view ItemCatalog website, run the following command.  :
```
python application.py
```

Note : Application is developed with basic css. But every functionality should work
