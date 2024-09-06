from datetime import datetime
import os
import json

import requests

from active_context import base_user_folder
from errors import TileExistsError


async def register_user(user_id):
    try:
        path = f"{base_user_folder}{user_id}"
        file_exists = os.path.isdir(path)

        if not file_exists:
            os.mkdir(path)

            # Specify the path to point to a json-file
            path = path + '/user_details.json'

            with open(path, "a+") as f:
                data = {
                    'user_details': [
                        {
                            'name': user_id,
                            'created': datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        }
                    ]
                }

                json_string = json.dumps(data)
                f.write(json_string)
    except Exception as e:
        print(e)


async def create_submit_entry(path, tile):
    path = path + '/entries.json'
    file_exists = os.path.isfile(path)

    # If file exists, append the new entry to the json file,
    # If no entries exist, create the json-file.
    if file_exists:
        with open(path, 'r') as json_file:
            data = json.load(json_file)

        tile_exists = False
        found_tile_index = -1

        for index, entry in enumerate(data['entries']):
            if entry['tile'] == tile:
                tile_exists = True
                found_tile_index = index
                break

        if tile_exists:
            raise TileExistsError("Tile already exists for that id.")

        if not tile_exists:
            data['entries'].append({
                'tile': tile,
                'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            })
        else:
            data['entries'][found_tile_index]['tile'] = tile
            data['entries'][found_tile_index]['submitted'] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

        with open(path, 'w') as json_file:
            json_string = json.dumps(data)
            json_file.write(json_string)
    else:
        with open(path, "a+") as f:
            data = {
                'entries': [
                    {
                        'tile': tile,
                        'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    }
                ]
            }

            json_string = json.dumps(data)
            f.write(json_string)


async def save_image(ctx, submitter_id, tile, image_url):
    path = f"{base_user_folder}{submitter_id}"

    try:
        img_data = requests.get(image_url).content
    except Exception:
        await ctx.response.send_message("No image provided, entry must have an image attached", ephemeral=True)
        return

    await create_submit_entry(path, tile)

    # If the account exists, create an image entry of the submission
    with open(path + '/' + str(tile) + '.jpg', 'wb') as handler:
        handler.write(img_data)
        handler.truncate()


def mention_user(user_id: int):
    return f'<@{user_id}>'


def get_completed_lines(matrix, as_data=False):
    fully_completed_rows = [row for row in matrix if all(cell == 'X' for cell in row)]
    fully_completed_columns = [list(column) for column in zip(*matrix) if all(cell == 'X' for cell in column)]
    fully_completed_diagonals = []

    main_diagonal = [matrix[i][i] for i in range(min(len(matrix), len(matrix[0]))) if matrix[i][i] == 'X']
    if len(main_diagonal) == min(len(matrix), len(matrix[0])):
        fully_completed_diagonals.append(main_diagonal)

    anti_diagonal = [matrix[i][len(matrix[0]) - 1 - i] for i in range(min(len(matrix), len(matrix[0]))) if matrix[i][len(matrix[0]) - 1 - i] == 'X']
    if len(anti_diagonal) == min(len(matrix), len(matrix[0])):
        fully_completed_diagonals.append(anti_diagonal)

    if as_data:
        return [len(fully_completed_rows), len(fully_completed_columns), len(fully_completed_diagonals)]
    return f'Rows completed: {len(fully_completed_rows)}', f'Columns completed: {len(fully_completed_columns)}', f'Diagonals completed: {len(fully_completed_diagonals)}'