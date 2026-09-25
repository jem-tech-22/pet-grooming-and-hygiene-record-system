from database.database import DatabaseManager
from managers.pet_manager import PetManager
from models.pet import Pet


def describe_pet(pet):
    return (
        f"Name: {pet.name}, Species: {pet.species}, "
        f"Breed: {pet.breed}, Age: {pet.age}, Owner: {pet.owner}"
    )


def run_test():
    database_manager = DatabaseManager()
    pet_manager = PetManager(database_manager)
    bruno = None
    delete_completed = False

    try:
        print("CREATE")
        try:
            bruno = Pet(
                name="Bruno",
                species="Dog",
                breed="Golden Retriever",
                age=3,
                owner="Juan"
            )
            bruno = pet_manager.create_pet(bruno)
            print(f"PASS: Bruno created with ID {bruno.id}")
        except Exception as error:
            print(f"FAIL: Could not create Bruno: {error}")

        print("\nREAD")
        try:
            read_pet = pet_manager.get_pet_by_id(bruno.id)
            if read_pet is not None:
                print(f"PASS: Bruno retrieved - {describe_pet(read_pet)}")
            else:
                print("FAIL: Bruno could not be retrieved")
        except Exception as error:
            print(f"FAIL: Could not read Bruno: {error}")

        print("\nUPDATE")
        try:
            bruno.age = 4
            update_succeeded = pet_manager.update_pet(bruno)
            updated_pet = pet_manager.get_pet_by_id(bruno.id)
            if update_succeeded and updated_pet is not None and updated_pet.age == 4:
                print(f"PASS: Bruno age updated to {updated_pet.age}")
            else:
                print("FAIL: Bruno age was not updated to 4")
        except Exception as error:
            print(f"FAIL: Could not update Bruno: {error}")

        print("\nSEARCH")
        try:
            matching_pets = pet_manager.search_pets("Bruno")
            if matching_pets:
                print("PASS: Bruno found in search results")
                for matching_pet in matching_pets:
                    print(f"  {describe_pet(matching_pet)}")
            else:
                print("FAIL: Bruno was not found in search results")
        except Exception as error:
            print(f"FAIL: Could not search for Bruno: {error}")

        print("\nDELETE")
        try:
            delete_succeeded = pet_manager.delete_pet(bruno.id)
            delete_completed = delete_succeeded
            deleted_pet = pet_manager.get_pet_by_id(bruno.id)
            if delete_succeeded and deleted_pet is None:
                print("PASS: Bruno deleted and no longer exists")
            else:
                print("FAIL: Bruno still exists after deletion")
        except Exception as error:
            print(f"FAIL: Could not delete Bruno: {error}")
    finally:
        if bruno is not None and not delete_completed:
            pet_manager.delete_pet(bruno.id)
        database_manager.close()


if __name__ == "__main__":
    run_test()