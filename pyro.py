from imdb import IMDb, Cinemagoer
import pyrogram
from pyrogram import filters, types


api_id = ''
api_hash = ''
bot_token = ''

app = pyrogram.Client('my_account', api_id, api_hash, bot_token=bot_token)

def imdbRes(query: str,audio:str):
    try:
        ia = IMDb()
        search_results = ia.search_movie(query)
        buttons = []

        if search_results:
            for movie in search_results[:5]:  # Limit results to 5
                imdb_id = movie.movieID
                year = movie.get('year', 'N/A')  # Use get to avoid missing year errors
                imdb_link = f"poster https://www.imdb.com/title/tt{imdb_id}/ {audio}"
                button = [types.InlineKeyboardButton(f"{movie['title']} ({year})", callback_data=imdb_link)]
                buttons.append(button)
                
        return buttons  # Always return a list, even if it's empty

    except Exception as e:
        print(f"Error in imdbRes: {e}")
        return []  # Return an empty list in case of an error
    

@app.on_message(filters.regex(r"^/custom-(.+)-(.+)$"))
async def custom_handler(client, message):
    # Extract fileName and linkHere from the matched groups
    fileName = message.matches[0].group(1)
    linkHere = message.matches[0].group(2)

    # Creating inline keyboard with the provided link
    reply_markup = types.InlineKeyboardMarkup(
        [
            [types.InlineKeyboardButton("Click here to search", url=linkHere)]
        ]
    )

    # Sending message with bold fileName and reply markup
    await message.reply_text(
        f"**{fileName}**",
        reply_markup=reply_markup
    )



@app.on_message(filters.regex(r'^/post/(.+)/(.+)$'))
async def post_handler(client, message):
    try:
        file_name, language = message.text.split('/')[2:]
        buttons = imdbRes(file_name,language)

        if buttons:
            reply_markup = types.InlineKeyboardMarkup(buttons)
            await app.send_message(message.chat.id, "Choose a Movie", reply_markup=reply_markup)
        else:
            await app.send_message(message.chat.id, "No Results FOUND !!")
       
    except Exception as e:
        await client.send_message(message.chat.id, f'Error: {str(e)}')


@app.on_callback_query()
async def callBackHandler(client,callback_query):
    data= callback_query.data
    print(callback_query)

    if data.startswith("poster"):
        postInfo = data.split(" ")

        print(postInfo)

        ia = Cinemagoer()

        imdbId = postInfo[1].split("/title/tt")[-1].split("/")[0]

        print(imdbId)

        movie = ia.get_movie(imdbId)

        if movie:
            title = movie.get('title')
            year = movie.get('year')
            rating = movie.get('rating')
            genres = movie.get('genres',[])

            print(title,year,rating,genres)

            await client.send_message(
                callback_query.from_user.id,
                f"✅ <b>{title}\n\n🔊{postInfo[2]}\n\n⭐️ <a href='{postInfo[1]}'>IMDB Info</a>\n\n Genres: {' '.join(genres)}</b>",
                parse_mode=pyrogram.enums.ParseMode.HTML,
                reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("Yes", callback_data=f"post_yes_imdb-{imdbId}-{postInfo[2]}"),
                    types.InlineKeyboardButton("No", callback_data="post_no_imdb")
                ]
            ]))
            
    elif data.startswith("post_yes_imdb"):

        imdbInfo = data.split('-')

        ia = Cinemagoer()

        movie = ia.get_movie(imdbInfo[1]);

        if movie:

            await client.send_message('7822087230',   f"✅ <b>{movie.get('title')}\n\n🔊{imdbInfo[2]}\n\n⭐️ <a href='https://www.imdb.com/title/tt{imdbInfo[1]}'>IMDB Info</a>\n\n Genres: {' '.join(movie.get('genres',[]))}</b>",
            reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("Click Here to Search", url=f"https://t.me/bot?start=getfile-")
                ]
            ])
            )
       







app.run()
