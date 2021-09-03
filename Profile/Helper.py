#-*- coding: utf-8 -*-

from typing import Optional, Union, Dict, List

from Common import *
from DeckList.Helper import *

Profile = Dict[str, Optional[str]]

class Profiles:
	def __init__(self):
		self.List: List[Profile] = toGen(db['prof'])
		for idx in range(len(self.List)):
			if self.List[idx]['cls2'] == 'None':
				self.List[idx]['cls2'] = None

	def append(self, ID: Union[str, int], arg1: str, arg2: str) -> None:
		if '&' in arg1:
			classs = arg1.split('&')
			self.List.append({
				'id': str(ID),
				'cls1': strToClass(classs[0]),
				'cls2': strToClass(classs[1])
			})
		elif arg2 in classes.keys():
			self.List.append({
				'id': str(ID),
				'cls1': strToClass(arg1),
				'cls2': strToClass(arg2)
			})
		elif arg2 == 'None':
			self.List.append({
				'id': str(ID),
				'cls1': strToClass(arg1),
				'cls2': None
			})
		else:
			self.List.append({
				'id': str(ID),
				'cls1': strToClass(arg1),
				'cls2': None
			})
		db['prof'] = self.List

	def find(self, user: discord.User) -> Optional[Profile]:
		tar = [prof for prof in self.List if prof['id'] == str(user.id)]
		return tar[0] if tar else None
	
	def isin(self, user: discord.User) -> bool:
		return len([prof for prof in self.List if prof['id'] == str(user.id)]) > 0
	
	def get(self, tar: discord.User, lang: Lang) -> discord.Embed:
		if tar.bot:
			embed = discord.Embed(
				title=f'{tar.display_name}의 프로필입니다!' if lang == 'KR' else f"{tar.display_name}'s profile!",
				color=tar.color
			)
			embed.set_thumbnail(url=tar.avatar_url)

			embed.add_field(
				name='만든 사람' if lang == 'KR' else 'Maker',
				value=f'<@!{maker[tar.id]}>',
				inline=False
			)
			embed.add_field(
				name='만든 날짜' if lang == 'KR' else 'Birthday',
				value=madeDate[tar.id],
				inline=False
			)

			return embed
		else:
			profile = self.find(tar)
			embed = discord.Embed(
				title=f'{tar.display_name}님의 프로필입니다!' if lang == 'KR' else f"{tar.display_name}'s profile!",
				color=tar.color
			)
			embed.set_thumbnail(url=tar.avatar_url)

			embed.add_field(
				name="주력 클래스" if lang == 'KR' else "Main Class",
				value=(profile['cls1'] if not profile['cls2'] else f"{profile['cls1']}, {profile['cls2']}") if profile\
                    else ("프로필이 등록되어있지 않습니다" if lang == 'KR' else "Profile is not Enrolled"),
				inline=False
			)
			embed.add_field(
				name='추가한 로테이션 덱(이번 팩)' if lang == 'KR' else "His or Her Deck in Rotation(This pack)",
				value=dList.GetCount(tar.id, 'RT'),
				inline=False
			)
			embed.add_field(
				name='추가한 언리미티드 덱' if lang == 'KR' else "His or Her Deck in Unlimited",
				value=dList.GetCount(tar.id, 'UL'),
				inline=False
			)
			return embed
		
profiles = Profiles()
