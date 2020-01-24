import os
import itchat

itchat.login()

friends = itchat.get_friends(update=True)

base_folder = 'wechat'
if os.path.isdir(base_folder):
    pass
else:
    os.mkdir(base_folder)

for item in friends:
    img = itchat.get_head_img(item['UserName'])

    # 使用用户昵称作为文件名
    path = os.path.join(base_folder, '{}.jpg'.format(item['NickName'].replace('/', '')))
    with open(path, 'wb') as f:
        f.write(img)
    print('{} 写入完成...'.format(item['NickName']))