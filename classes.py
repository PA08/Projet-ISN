import pygame, random, graphics
from pygame.locals import *



#self.image = pygame.Surface((width, height))
#self.image.fill(color)

class Player(pygame.sprite.Sprite): #Classe joueur

	def __init__(self, x, y, isRight, up, left, right, gun, imgR, imgL, imgFR, imgFL, jump, fire):
		super(Player, self).__init__()

		#PARAMETRES

		if isRight == True: self.image = imgR
		else: self.image = imgL
		self.imgR = imgR
		self.imgL = imgL
		self.imgFR = imgFR
		self.imgFL = imgFL
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y
		self.spawnX, self.spawnY = x, y
		self.xspeed, self.yspeed = 0, 0
		self.speed = 5
		self.speedX = 5
		self.speedY = self.speedX * 3.5
		self.score = 0
		self.life = 100
		self.lifeBar = pygame.Surface((self.life * 2 + 1, 12))
		self.lifeBar.fill((10, 250, 10))
		self.jump = jump
		self.fire = fire
		self.isRight = isRight
		self.up = up
		self.left = left
		self.right = right
		self.gun = gun
		self.enemy = 0

	#METHODES

	def setEnemy(self, enemy):
		self.enemy = enemy

	def update(self, collidable = pygame.sprite.Group()): #méthode gérant les collisions et la gravité

		self.gravity() # appel de la fonction qui met en place la gravité

		self.rect.x += self.xspeed # on incrémente toujours la coordonnée x de la vitesse x (de base à 0 : le joueur n'avance pas)

		collisionList = pygame.sprite.spritecollide(self, collidable, False) #liste contenant toutes les collisions en train de se faire

		for collided in collisionList: #On parcours la liste des collisions pour gérer l'arrêt du joueur en cas de contact horizontal
			if self.xspeed > 0:
				self.rect.right = collided.rect.left # : stoppe le joueur
			if self.xspeed < 0:
				self.rect.left = collided.rect.right # : idem

		self.rect.y += self.yspeed # idem comme pour la coordonnée x

		collisionList = pygame.sprite.spritecollide(self, collidable, False) # idem vertical

		for collided in collisionList:
			if self.yspeed > 0:
				self.rect.bottom = collided.rect.top
				self.yspeed = 0
			if self.yspeed < 0:
				self.rect.top = collided.rect.bottom
				self.yspeed = 0

		if self.life <= 0: # system de réaparition si le joueur n'a plus de vie
			self.die()

	def render(self, screen,sx, sy, lsx, lsy, lx, ly, lifeBarSupport):

		screen.blit(self.image, (self.rect.x, self.rect.y))

		self.drawLifeBar(screen, lsx, lsy, lx, ly, lifeBarSupport)

		self.drawScore(screen , sx, sy)

	def gravity(self, gravity = 1): #méthode de gravité
		if self.yspeed == 0: # si le joueur est immobile, la gravité ne l'affecte pas
			self.yspeed = 1
		else:
			self.yspeed += gravity # sinon oui

	def drawLifeBar(self, screen, x, y, xx, yy, lifeBarSupport): #méthode affichage de la vie
		if self.life <= 0:
			self.lifeBar = pygame.Surface((0, 12)) # si la vie est inférieure à 0 on créé un rectange null
		else:
			self.lifeBar = pygame.Surface((self.life * 2 + 1, 12)) # sinon on crée un rectangle dont la longeur varie en fonction de la vie
		self.lifeBar.fill((10, 250, 10))
		screen.blit(lifeBarSupport, (x, y))
		screen.blit(self.lifeBar, (xx, yy))

	def drawScore(self, screen, x, y):
		screen.blit(graphics.score[self.score], (x, y))

	def addScore(self, number):
		self.score += number

	def addLife(self, life):
		self.life += life
		if self.life > 100:
			self.life = 100

	def setSpeed(self, speed):
		self.speedX = speed

	def hit(self, damage): # méthode pour prendre des dégâts
		self.life -= damage

	def die(self): # méthode de réaparition
		self.life = 100
		self.enemy.addScore(1)
		self.enemy.addLife(25)
		self.rect.x, self.rect.y = self.spawnX, self.spawnY

class Block(pygame.sprite.Sprite): # classe bloc

	def __init__(self, x, y, img):
		super(Block, self).__init__()

		#PARAMETRES

		self.image = img
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y

class Map(object): #classe map

	def __init__(self, level):
		super(Map, self).__init__()

		#PARAMETRES

		self.blockList = pygame.sprite.Group()
		self.level = level

	#METHODES

	def generate(self): # méhode générant un terrain à partir d'un fichier
		with open(self.level, 'r') as level: #on parcours le fichier

			y = 0

			for lines in level:
				x = 0
				for car in lines:
					if car != '\n': # on ignore les retours à la ligne
						if car == "#": # si on trouve le caractère "#" On crée un objet bloc que l'on ajoute à une liste
							block = Block(x, y, graphics.block)
							self.blockList.add(block)
					x += 32
				y += 32

	def destroyAll(self):
		for block in self.blockList:
			self.blockList.remove(block)
			del block

		del self


class Bullet(pygame.sprite.Sprite): #classe balle
	bullets = pygame.sprite.Group()

	def __init__(self, x, y, speed, img):
		super(Bullet, self).__init__()

		#PARAMETRES

		self.image = img
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y
		self.speed = speed
		Bullet.bullets.add(self)

	#METHODES

	@staticmethod
	def move(): # méthode affectant toutes les instances de la classe Bullet permettant de les faires toutes bouger
		for bullet in Bullet.bullets:
			bullet.rect.x += bullet.speed

	def destroy(self): #méthode détruisant l'objet et en le supprimmant de la liste
		Bullet.bullets.remove(self)
		del self

	@staticmethod
	def destroyAll():
		for b in Bullet.bullets:
			b.destroy()

class Item(pygame.sprite.Sprite):
	itemList = pygame.sprite.Group()
	
	def __init__(self, x, y, img):
		super(Item, self).__init__()
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y
		Item.itemList.add(self)

	def destroy(self):
		Item.itemList.remove(self)
		ItemSpawner.available = True
		del self

	@staticmethod
	def destroyAll():
		for i in Item.itemList:
			i.destroy()

class LifeBonus(Item):
	
	def __init__(self, x, y, img, life):
		super(LifeBonus, self).__init__(x, y, img)
		self.life = life
	
	def setBonus(self, player):
 		player.addLife(self.life)

class SpeedBonus(Item):
	def __init__(self, x, y, img, speed):
		super(SpeedBonus, self).__init__(x, y, img)
		self.speed = speed

	def setBonus(self, player):
		player.setSpeed(self.speed)

	def disableBonus(self, player):
		player.setSpeed(self.speed / 2)


class ItemSpawner(object):
	available = True
	
	def __init__(self, time):
		super(ItemSpawner, self).__init__()

		self.time = time
		self.timerBonus = []

		self.speedBonus = 0

		self.timer = 0
		

	def update(self, gameTime, player1, player2):
		
		if gameTime % self.time == 0 and self.available == True:
			self.spawnItem(1, gameTime)
			ItemSpawner.available = False

		if player1.speedX != 5:

			self.timerBonus.append(gameTime)
			if self.timerBonus[-1] - self.timerBonus[0] == 5:
				self.speedBonus.disableBonus(player1)

		if player2.speedX != 5:
			self.timerBonus.append(gameTime)
			if self.timerBonus[-1] - self.timerBonus[0] == 5:
				self.speedBonus.disableBonus(player2)




	def spawnItem(self, typ, gameTime):
		rdm = random.randint(0, 3)
		
		if random.randint(0, 1):
 			lifeBonus = LifeBonus(graphics.area[rdm][0], graphics.area[rdm][1], graphics.lifeBonus, 50)
		else:
 			self.speedBonus = SpeedBonus(graphics.area[rdm][0], graphics.area[rdm][1], graphics.speedBonus, 10)


		