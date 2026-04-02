import urllib.parse

api_key = "AIzaSyAAJL11FGR1AImjuxi9kYcxmBTovEZqS7s"
map_addr = "Fasteign, Iceland"
map_addr_encoded = urllib.parse.quote(map_addr)
static_map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={map_addr_encoded}&zoom=15&size=600x200&scale=2&maptype=roadmap&markers=color:red%7C{map_addr_encoded}&key={api_key}"
print(static_map_url)
