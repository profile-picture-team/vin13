"""

	Это очень полезный модуль
	Он делает вот так:

	(∩ᄑ_ᄑ)⊃━☆ﾟ*･｡*･:≡( ε:)
"""

# циганские фокусы
folder = __file__[:-11]
import sys
sys.path.insert(0, folder)

from Playlist import Playlist
from MusicInfo import MusicInfo
from MusicSearch import VkSearch

del sys.path[0]