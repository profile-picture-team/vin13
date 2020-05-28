"""

	Это очень полезный модуль
	Он делает вот так:

	(∩ᄑ_ᄑ)⊃━☆ﾟ*･｡*･:≡( ε:)
"""

# циганские фокусы
folder = __file__[:-11]
import sys
sys.path.insert(0, folder)

from PlaylistManager import PlaylistManager
from Playlist import Playlist
from MusicInfo import MusicInfo
import MusicSearch

del sys.path[0]