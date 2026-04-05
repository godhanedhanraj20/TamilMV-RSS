with open("bot.py", "r") as f:
    content = f.read()

content = content.replace('        text = "**Top Results:**\n\n"\n', '        text = "**Top Results:**\\n\\n"\n')
content = content.replace('            text += f"**{i}.** {title}\n"\n', '            text += f"**{i}.** {title}\\n"\n')
content = content.replace('            text += f"Size: {res[\'size\']}\n"\n', '            text += f"Size: {res[\'size\']}\\n"\n')
content = content.replace('            text += f"Link: {res[\'link\']}\n\n"\n', '            text += f"Link: {res[\'link\']}\\n\\n"\n')

with open("bot.py", "w") as f:
    f.write(content)
