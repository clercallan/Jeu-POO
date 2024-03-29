import copy
import math
import random
from tkinter import *
# from playsound import playsound
from PIL import Image, ImageTk
from abc import ABC, abstractmethod
import winsound
# exceptions

def sign(x):
    if x > 0:
        return 1
    return -1


class Coord(object):
    """Implementation of a map coordinate"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return '<' + str(self.x) + ',' + str(self.y) + '>'

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def distance(self, other):
        """Returns the distance between two coordinates."""
        d = self - other
        return math.sqrt(d.x * d.x + d.y * d.y)

    cos45 = 1 / math.sqrt(2)

    def direction(self, other):
        """Returns the direction between two coordinates."""
        d = self - other
        try:
            cos = d.x / self.distance(other)
        except ZeroDivisionError:
            cos=d.x/self.distance(other)+1
        if cos > Coord.cos45:
            return Coord(-1, 0)
        elif cos < -Coord.cos45:
            return Coord(1, 0)
        elif d.y > 0:
            return Coord(0, -1)
        return Coord(0, 1)


class Element(ABC):
    """Base class for game elements. Have a name."""
    def __init__(self, name, abbrv=""):
        self.name = name
        if abbrv == "":
            abbrv = name[0]
        self.abbrv = abbrv

    def __repr__(self):
        return self.abbrv

    def description(self):
        """Description of the element"""
        return "<" + self.name + ">"
    
    @abstractmethod
    def meet(self, hero):
        """Makes the hero meet an element. Not implemented. """
        raise NotImplementedError('Abstract Element')

class Equipment(Element):
    """A piece of equipment"""
    def __init__(self, name, abbrv="", usage=None,nonShop=True,price=0):
        Element.__init__(self, name, abbrv)
        self.usage = usage
        self.nonShop=nonShop
        self.price=price

    def meet(self, hero):
        """Makes the hero meet an element. The hero takes the element."""
        if self.price==9999 :
            if theGame().thief is False:
                theGame().addMessage("Take a look !\n")
            else:
                theGame().addMessage("My brothers will get you !\n")
            return False
        if self.price==9998:
            c=theGame().floor.pos(self)
            theGame().floor.rm(c)
            if random.randrange(9)<5:
                theGame().floor.put(c,Creature('Mimic',25,abbrv='Mimic',strength=8,xp=20))
                return False
            theGame().floor.put(c,theGame().randMimicLoot())
            return False
        if self.nonShop or theGame().thief:
           if len(theGame().hero._inventory)<5:
                hero.take(self)
                theGame().addMessage("You pick up a " + self.name)
                return True
        if hero.banque>=self.price:
                hero.banque-=self.price
                hero.take(self)
                theGame().addMessage("You buy a " + self.name)
                return True           
        if not self.nonShop :           

            theGame().addMessage('Not enough money !\n Price : ' + str(self.price) + ' Dogecoins \n')
            theGame().steal+=1
            if theGame().steal==5:
                rng = random.randint(1,2)
                if rng == 1:
                    theGame().addEffect('You filthy thief !\n')
                if rng == 2:
                    theGame().addEffect('Stop right there criminal scum !\n')
                theGame().thief=True
                hero.take(self)
                if rng == 2 :
                    window.unbind('<KeyPress>')
                    #playsound(r'musique jeu\criminal.wav')
                theGame().steal=0
                return True
        return False
    
    def use(self, creature):
        """Uses the piece of equipment. Has effect on the hero according usage.
            Return True if the object is consumed."""
        if self.usage is None:
            if isinstance(creature, Hero):
                theGame().addMessage("The " + self.name + " is not usable \n")
                return False
            else:
                creature.hp-=50
        else: ### à modifier pour le Moonstaff False
            theGame().addMessage('You used ' + self.name + '\n')
            return self.usage(self, creature)

class Season:
    def spring(self): 
        theGame().hero.sick = True
        theGame().hero.starve = 1
        if theGame().level < 7:
            return True
        return False
        #### plus de bouffe
    
    def summer(self):
        theGame().hero.starve = 4
        theGame().hero.sick = False
        if 7<=theGame().level<15:
            return True
        return False
    
    def fall(self):
        theGame().hero.starve = 2
        theGame().hero.sick=False
        if 15<=theGame().level<20:
            return True
        return False
    
    def winter(self):
        theGame().hero.starve = 1
        theGame().hero.sick = True
        if theGame().level >=20:
            return True
        return False
    
    def drawSeason(self):
        if theGame().level < 7:
            canvasInventaire.create_image(360,940, anchor = NW, image = textures['season']['spring'])
            canvasInventaire.create_image(510,940, anchor = NW, image = textures['season']['spring'])
            canvasInventaire.create_text(450,960, text = 'Spring', font = 'Arial 25', fill = 'green')

        if 7<=theGame().level<15:
            canvasInventaire.create_image(330,935, anchor = NW, image = textures['season']['summer'])
            canvasInventaire.create_text(450,960, text = 'Summer', font = 'Arial 25', fill = 'red')
        elif 15<=theGame().level<23:
            canvasInventaire.create_image(375,935, anchor = NW, image = textures['season']['fall'])
            canvasInventaire.create_image(482,935, anchor = NW, image = textures['season']['fall'])
            canvasInventaire.create_text(450,960, text = 'Fall', font = 'Arial 25', fill = 'orange')

        elif theGame().level >=23:
            canvasInventaire.create_image(350,935, anchor = NW, image = textures['season']['winter'])
            canvasInventaire.create_image(497,935, anchor = NW, image = textures['season']['winter2'])
            canvasInventaire.create_text(450,960, text = 'Winter', font = 'Arial 25', fill = 'cyan')

class Food(Equipment):
    """Food"""
    def __init__(self, name, abbrv = '', usage = None, nonShop=True,price=0):
        Equipment.__init__(self, name, abbrv, usage, nonShop,price)
    
    def use(self, creature):
        theGame().addMessage('You consumed the ' + self.name  + '\n')
        return self.usage(self, creature)

class MegaMetal(ABC):
    def __init__(self, name, abbrv =''):
        Equipment.__init__(self,name,abbrv)
    
    @abstractmethod
    def meet():
        pass

class Metal(Equipment, MegaMetal):
    """Metal"""
    def __init__(self,name,abbrv = '', attack = 0, usage = None, nonShop=True,price=0):
        Equipment.__init__(self,name,abbrv,nonShop,price)
        self.usage = usage
        self.attack = attack
    
    def use(self, creature):
        """Uses the piece of equipment. Has effect on the hero according usage.
            Return True if the object is consumed."""
        theGame().addMessage("The " + creature.name + " uses the " + self.name)
        return self.usage(self, creature)
          

class MetallicProjectile(MegaMetal,Element):
    """Projectiles used for guns"""
    def __init__(self,name,abbrv = '', dmg = 20, nonShop = True):
        self.name = name
        self.abbrv = abbrv
        self.dmg = dmg
        self.nonShop = nonShop
        
    
    def meet(self,hero):
        hero.takeProjectile(self)
        theGame().addMessage("You pick up a " + self.name + '\n')
        return True
    
    def drawProjectilesInventaire(self):
        cptBee = 0
        stock = (str(i) for i in theGame().hero._stock)
        for j in stock:
            if j == 'Bee':
                cptBee+=1

        canvasInventaire.create_image(325,755, anchor = NW, image = textures['interface']['Kills'])
        canvasInventaire.create_image(520,760, anchor = NW, image = textures['items']['Bee'])

        if theGame().hero.otherDim:
            canvasInventaire.create_text(430,790, text = '???' , font = 'Arial 30')
            canvasInventaire.create_text(630,790, text = '???' , font = 'Arial 30') 
 
        else:
            canvasInventaire.create_text(430,790, text = 'X ' + str(theGame().hero.kill) , font = 'Arial 30')
            canvasInventaire.create_text(630,790, text = 'X ' + str(cptBee) , font = 'Arial 30') 
 
    
    def setdmg(self):
        if 'Gun' in (str(i) for i in theGame().hero.sword):
            self.dmg = 20 + math.floor(theGame().hero.strength/5)
        elif 'Bodyguard 638' in (str(i) for i in theGame().hero.sword):
            self.dmg = 30 + math.floor(theGame().hero.strength/2)

            
class Sword(Equipment):
    """Swords"""
    def __init__(self, name, abbrv= '',attack = 10, usage = None, nonShop=True,price=0):
        Equipment.__init__(self, name, abbrv, usage, nonShop,price)
        self.attack = attack
        self.usage = usage
    
    def use(self, creature):
        theGame().addMessage('You equipped ' + self.name + '. Strength +' +  str(self.attack) + '\n')
        return self.usage(self,creature)
    
    def drawEquippedSword(self):
        canvasInventaire.create_image(495,170, anchor = NW, image = textures['interface']['Strength'])
        if theGame().hero.otherDim:
            canvasInventaire.create_text(535,180, text = '???', font = "Arial 12", fill = 'red')
        else:
            canvasInventaire.create_text(535,180, text = str(theGame().hero.strength), font = "Arial 12", fill = 'red')
        for i in theGame().hero.sword:
            if i.abbrv == 'Rainbow Sword':
                canvasInventaire.create_image(500,100, anchor = NW, image = textures['items']['Rainbow Sword'])
            if i.abbrv == 'Katana':
                canvasInventaire.create_image(500,100, anchor = NW, image = textures['items']['Katana'])
            if i.abbrv == 'Gun':
                canvasInventaire.create_image(500,100, anchor = NW, image = textures['items']['Gun'])
            if i.abbrv == 'Bodyguard 638':
                canvasInventaire.create_image(500,100, anchor = NW, image = textures['items']['Smith&Wesson'])


class Armor(Equipment):
    """Armors"""
    def __init__(self,name, abbrv = '', armor = 10,usage = None, nonShop=True,price=0):
        Equipment.__init__(self, name, abbrv, usage, nonShop,price)
        self.usage = usage
        self.armor = armor
    
    def use(self, creature):
        theGame().addMessage('You equipped ' + self.name + '. Armor +' +  str(self.armor) + '\n')
        return self.usage(self,creature)
    
    def drawEquippedArmor(self):
        canvasInventaire.create_image(588,168, anchor = NW, image = textures['interface']['Shield'])
        if theGame().hero.otherDim:
            canvasInventaire.create_text(625,180, text = '???', font = "Arial 12", fill = 'red')
        else:
            canvasInventaire.create_text(625,180, text = str(theGame().hero.protection), font = "Arial 12", fill = 'red')
        for i in theGame().hero.armor:
            if i.abbrv == 'Blue Armor':
                canvasInventaire.create_image(580,95, anchor = NW, image = textures['items']['Blue Armor'])
            
            if i.abbrv == 'Iron Armor':
                canvasInventaire.create_image(595,105, anchor = NW, image = textures['items']['Iron Armor'])

class Creature(Element):
    """A creature that occupies the dungeon.
        Is an Element. Has hit points and strength."""
    
    def __init__(self, name, hp, hpMax=10, abbrv="", strength=1, xp = 1, on=None):
        Element.__init__(self, name, abbrv)
        self.hpMax = hpMax
        self.hp = hp
        self.bonus = 0
        self.strength = strength
        self.xp = xp
        self.on = on

    def description(self):
        """Description of the creature"""
        return Element.description(self) + "(" + str(self.hp) + ")"

    def meet(self, other):
        """The creature is encountered by an other creature.
            The other one hits the creature. Return True if the creature is dead."""
        if isinstance(self, Hero):
            if theGame().hero.protection > other.strength:
                self.hp-=1
            else:
                self.hp -= other.strength - theGame().hero.protection
        else:
            self.hp -= other.strength
        
        if str(other.abbrv) == 'Metallica':
            for j in theGame().hero._inventory:
                if isinstance(j, MegaMetal):
                    theGame().hero._inventory.remove(j)
            theGame().addEffect("Metallica destroyed your metallic stuff !\n" )
            for i in theGame().hero._stock:
                if isinstance(i, MegaMetal):
                    theGame().hero._stock.remove(i)
            theGame().addEffect("Metallica destroyed your metallic ammos !\n")
        
        if str(other.abbrv) == 'C-Moon':
            window.unbind('<KeyPress>')
            theGame().cFloor()
        theGame().addMessage(other.name + " hits the " + self.name + '\n')
        if self.hp > 0:
            return False
        return True
    
    def use(self, elem):
        """Uses the piece of equipment. Has effect on the hero according usage.
            Return True if the object is consumed."""
        if elem.usage is None:
            self.hp-=10
            return False
        else:
            elem.use(self)

class Money(Element):
    """Money"""
    def __init__(self,name, abbrv, value = 1):
        Element.__init__(self, name, abbrv)
        self.value = value

    def meet(self,hero):
        hero.takeMoney(self)
        return True
    
    def showMoney(self):
        canvasInventaire.create_image(90,740, anchor = NW, image = textures['interface']['money'])
        if theGame().hero.otherDim:
            canvasInventaire.create_text(230,790, text = '???' , font = 'Arial 30')
        else:
            canvasInventaire.create_text(230,790, text = 'X ' +str(theGame().hero.banque) , font = 'Arial 30')

class Hero(Creature):
    """The hero of the game.
        Is a creature. Has an inventory of elements. """
    def __init__(self,
                 on = None,
                 name="Hero",
                 hp=10,
                 hpMax=70,
                 abbrv="@",
                 strength=5,
                 protection = 0,
                 xp=0,
                 lvl=1,
                 dist = 3):
        Creature.__init__(self, name, hp, hpMax, abbrv, strength, on)
        self.dist = dist
        self.hunger = 100
        self.starve = 2
        self.faim = 0
        self.kill = 0
        self.protection = protection
        self.xp = xp
        self.lvl = lvl
        self._inventory = []
        self.banque = 0
        self._bag=[]
        self._stock = []
        self.sword = [] ### liste de longueur 1 max
        self.armor = [] ### liste de longueur 1 max
        self.sickness = 0
        self.sick = False
        self.invisible = None
        self.equipped = False
        self.armored = False
        self.otherDim = False
        self.meetStairs = False
    def description(self):
        """Description of the hero"""
        return Creature.description(self) + str(self._inventory)

    def fullDescription(self):
        ""r"Complete description of the hero"""
        res = ''
        for e in self.__dict__:
            if e[0] != '_':
                res += '> ' + e + ' : ' + str(self.__dict__[e]) + '\n'
        res += '> INVENTORY : ' + str([x.name for x in self._inventory])
        return res

    def checkEquipment(self, o):
        ""r"Check if o is an Equipment."""
        if not isinstance(o, Equipment):
            raise TypeError('Not a Equipment')
    
    def checkMoney(self, el):
        if not isinstance(el, Money):
            raise TypeError('This is not money')
        return True

    def take(self, elem):  ### ajoute elem à l'inventaire du héro
    
        self.checkEquipment(elem)
        if len(self._inventory)<5:
            self._inventory.append(elem)
        return True
    
    def takeMoney(self, money):
        if self.checkMoney(money):
            theGame().hero.banque+=1
    
    def checkKids(self, kids):
        if not isinstance(kids, Kids):
            raise TypeError('Not a Kid')
    
    def checkProjectile(self,el):
        if not isinstance(el, MetallicProjectile):
            raise TypeError('Not a projectile')

    def takeKids(self, kids):
        self.checkKids(kids)
        theGame().hero._bag.append(kids)
        theGame().addMessage('You picked up ' + str(kids) +  '\n')
    
    def takeProjectile(self, el):
        self.checkProjectile(el)
        theGame().hero._stock.append(el)

    def use(self, elem):
        """Use a piece of equipment"""
        self.checkEquipment(elem)
        if elem not in self._inventory:
            raise ValueError('Equipment ' + elem.name + 'not in inventory')
        if elem.use(self):
            if isinstance(elem, Metal) or isinstance(elem, Sword) or isinstance(elem, Armor):
                if isinstance(elem, Sword) or isinstance(elem, Metal):
                    theGame().addMessage('You gained ' + str(elem.attack) + 'strength \n')
                    self.sword.append(elem)
                if isinstance(elem, Armor):
                    theGame().addMessage('You gained ' + str(elem.armor) + 'armor \n')
                    self.armor.append(elem)
            self._inventory.remove(elem)
            if self.on != None :
                self.take(self.on[0])
                self.on = None
    
    def addXP(self,x) :
        """Add x XP's points to the hero"""
        self.xp += x
    
    def refreshXP(self) :
        """If the XP is big enough, the hero wins one level and gains strength and HP"""
        if self.xp >= (self.lvl+1)**2:
            for i in range(self.lvl,self.lvl+10) :
                if self.xp >= i**2 :
                    self.lvl+=1
                    self.xp -= i**2
                    self.strength+=2 + math.floor(self.lvl/7)
                    self.hpMax += 5
                    self.hp += 5 
                    if self.lvl%3==0:
                        self.protection += 1  
                else :
                    break
    
    def drawXp(self):
        self.refreshXP()
        
        canvasInventaire.create_text(180,700, text = 'XP', font = 'Arial 20')

        canvasInventaire.create_rectangle(100,680,700,650, fill ='black')
        canvasInventaire.create_rectangle(100,680,100+600*(self.xp/((self.lvl+1)**2)),650, fill ='cyan')
        canvasInventaire.create_image(650,625, anchor = NW, image = textures['interface']['circle'])
        if self.otherDim:
            canvasInventaire.create_text(692,666, text = '?', font = 'Arial 20')
        else:
            canvasInventaire.create_text(692,666, text = str(self.lvl), font = 'Arial 20')
        canvasInventaire.create_image(600,600, anchor = NW, image = textures['interface']['Monosuke'])
        canvasInventaire.create_image(480,600, anchor = NW, image = textures['interface']['Monophanie'])
        canvasInventaire.create_image(360,590, anchor = NW, image = textures['interface']['Monotaro'])
        canvasInventaire.create_image(240,600, anchor = NW, image = textures['interface']['Monodam'])
        canvasInventaire.create_image(120,600, anchor = NW, image = textures['interface']['Monokid'])


    def drawInventaire(self):
        l=50

        if self.otherDim is True:
            canvasInventaire.create_text(500,700, text = "?????", font = 'Arial 20')
        else:
            if theGame().level<8:
                canvasInventaire.create_text(500,700, text = "Gangsta's Paradise: "+str(theGame().level), font = 'Arial 20')
            elif 8<=theGame().level<13:
                canvasInventaire.create_text(500,700, text = 'Earth, Wind & Fire: '+str(theGame().level), font = 'Arial 20')
            elif 13<=theGame().level<20:
                canvasInventaire.create_text(500,700, text = 'Highway to Hell: '+str(theGame().level), font = 'Arial 20')
            elif theGame().level>=20:
                canvasInventaire.create_text(500,700, text = "Stairway to Heaven: "+str(theGame().level), font = 'Arial 20')


        canvasInventaire.create_image(430,280, anchor = NW, image = textures['interface']['WoU opacité'])
        if theGame().hero.take:
            canvasInventaire.create_text(200,50, text = 'Inventaire : ', font = 'Arial 20') #### affiche l'inventaire du héros en string
            for j in range(len(theGame().hero._inventory)):
                eq = theGame().hero._inventory[j]
                if eq.abbrv == 'Potion de vie':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Health Pot'])
                    l+=100
                if eq.abbrv == "Potion d'invisibilité":
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['items']['Invisible pot'])
                    l+=100
                if eq.abbrv == 'TNT':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['TNT'])
                    l+=100                                    
                if eq.abbrv == 'Moonstaff':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Moonstaff'])
                    l+=100
                if eq.abbrv == 'Gun':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Gun'])
                    l+=100       
                if eq.abbrv == 'Rainbow Sword':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Rainbow Sword'])
                    l+=100      
                if eq.abbrv == 'Apple':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['items']['Apple'])
                    l+=100      
                if eq.abbrv == 'Pizza':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['items']['Pizza'])
                    l+=100
                
                if eq.abbrv == 'Katana':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['items']['Katana'])
                    l+=100
                
                if eq.abbrv == 'Blue Armor':
                    canvasInventaire.create_image(140,l-20, anchor = NW, image = textures['items']['Blue Armor'])
                    l+=100

                if eq.abbrv == 'Iron Armor':
                    canvasInventaire.create_image(140,l-20, anchor = NW, image = textures['items']['Iron Armor'])
                    l+=100
                
                if eq.abbrv == 'Chicken' :
                    canvasInventaire.create_image(140,l, anchor = NW, image = textures['items']['Chicken'])
                    l+=100
                
                if eq.abbrv == 'Bodyguard 638':
                    canvasInventaire.create_image(140, l, anchor = NW, image = textures['items']['Smith&Wesson'])
                    l+=100

    
    def unequipped(self):
        if len(self._inventory) < 5:
            self._inventory.append(self.sword[0])
            self.strength-=self.sword[0].attack
            theGame().addMessage('You lost ' + str(self.sword[0].attack))
            self.sword.remove(self.sword[0])
        else:
            theGame().addMessage("Your inventory is full !\n")
        self.equipped = False 
    
    def unequippedArmor(self):
        if len(self._inventory) < 5:
            self._inventory.append(self.armor[0])
        if Season.summer(Season):
            self.protection-=self.armor[0].armor-5
        else:
            self.protection-=self.armor[0].armor
        theGame().addMessage('You lost ' + str(self.armor[0].armor) + '\n')
        self.armor.remove(self.armor[0])
        self.armored = False 

class Stairs(Element):
    def __init__(self, name, abbrv =''):
        Element.__init__(self,name, abbrv)
    
    def meet(self, other):
        theGame().hero.otherDim = False
        theGame().newFloor()
        theGame().hero.meetStairs = True
        return True

class Room(object):
    """A rectangular room in the map"""
    def __init__(self, c1, c2):
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return "[" + str(self.c1) + ", " + str(self.c2) + "]"

    def __contains__(self, coord):
        return self.c1.x <= coord.x <= self.c2.x and self.c1.y <= coord.y <= self.c2.y

    def intersect(self, other):
        """Test if the room has an intersection with another room"""
        sc3 = Coord(self.c2.x, self.c1.y)
        sc4 = Coord(self.c1.x, self.c2.y)
        return self.c1 in other or self.c2 in other or sc3 in other or sc4 in other or other.c1 in self

    def center(self):  ### renvoie les coordonnées du centre de la salle

        return Coord((self.c1.x + self.c2.x) // 2,
                     (self.c1.y + self.c2.y) // 2)

    def randCoord(self):  #### return une coordonnée random de la map

        return Coord(random.randint(self.c1.x, self.c2.x),
                     random.randint(self.c1.y, self.c2.y))

    def randEmptyCoord(
            self,
            map):  ##### return une coordonnée random de case vide de la map

        c = self.randCoord()
        while map.get(c) != Map.ground or c == self.center():
            c = self.randCoord()
        return c

    def decorate(
            self,
            map):  #### génère des objets et des mobs aléatoirement dans la map
        map.put(self.randEmptyCoord(map), theGame().randEquipment())
        map.put(self.randEmptyCoord(map), theGame().randMoney())
        map.put(self.randEmptyCoord(map), theGame().randAmmo())
        map.put(self.randEmptyCoord(map), theGame().randMonster())

    
    def Cdecorate(self, map):
        map.put(self.randEmptyCoord(map), theGame().randCMonster())

class Shop(Room):
    """Une salle dédiée à l'achat d'items"""
    def __init__(self, c):
        Room.__init__(self,c,c+Coord(4,3))

    def decorate(self,map):
        if map.get(self.center()+Coord(-1,0)) !=Map.ground:
            map.rm(self.center()+Coord(-1,0))
        map.put(self.center()+Coord(-1,0),theGame().randShopItem())
        
        if map.get(self.center()+Coord(1,0)) !=Map.ground:
            map.rm(self.center()+Coord(1,0))       
        map.put(self.center()+Coord(1,0),theGame().randShopItem())
        
        if not theGame().thief :
            if map.get(self.center()+Coord(0,1)) !=Map.ground:
                map.rm(self.center()+Coord(0,1)) 

            map.put(self.center()+Coord(0,1),Equipment('Merchant','MerchantIt',nonShop=False,price=9999))
        else :
            if map.get(self.center()+Coord(0,1)) !=Map.ground:
                map.rm(self.center()+Coord(0,1)) 

            map.put(self.center()+Coord(0,1),Creature('Merchant',200,abbrv='Merchant',strength=40,xp=1))
    
class Mimic(Room):
    def __init__(self,c):
        Room.__init__(self,c,c+Coord(2,2))

    def decorate(self,map):
        if map.get(self.center())==Map.ground:
            map.put(self.center(),Equipment('Mimic','MimicIt',nonShop=False,price=9998))     

class Kids(Element):
    """Kids to pick up"""
    def __init__(self, name, abbrv = " "):
        Element.__init__(self, name, abbrv)
    
    def meet(self,hero):
        hero.takeKids(self)
        self.upgrade()
        return True
    
    def upgrade(self):
        if theGame().Monophanie in theGame().hero._bag and theGame().Monosuke in theGame().hero._bag and theGame().Monotaro in theGame().hero._bag and theGame().Monokid in theGame().hero._bag and theGame().Monodam in theGame().hero._bag:
           theGame().hero._bag.clear()
           theGame().hero.hp+=50
           theGame().hero.hpMax+=50
           theGame().hero.strength+=5
           theGame().hero.protection+=2
           theGame().hero.hunger = 100
           theGame().hero.dist += 1
    


class Map(object):
    """A map of a game floor.
        Contains game elements."""

    ground = '.'  # A walkable ground cell
    dir = {
        'z': Coord(0, -1),
        's': Coord(0, 1),
        'd': Coord(1, 0),
        'q': Coord(-1, 0)
    }  # four direction user keys
    empty = ' '  # A non walkable cell
    stairs = 'stairs'
    chariot = ''
    WoU = ''
    def __init__(self, size=20, hero=None):
        self.size = size
        self._mat = []
        self._elem = {}
        self._rooms = []
        self._roomsToReach = []
        self.dist=3
        for i in range(size):
            self._mat.append([Map.empty] * size)
        if hero is None:
            hero = Hero()
        self.hero = hero
        self.generateRooms(1)
        self.addRoom(Shop(self.randCoordPlus(Coord(4,3))))
        if random.randrange(9)<4:
            self.addRoom(Mimic(self.randCoordPlus(Coord(2,2))))
        while len(self._roomsToReach) < 6:
            self.generateRooms(1)
        self.reachAllRooms()
        
        nb = random.randint(1,len(self._rooms)-1)
        b=self._rooms[nb].center()
        self.put(b, Game.element[0])
        
        for r in self._rooms:
            if self.hero.otherDim is False:
                r.decorate(self)
            else:
                r.Cdecorate(self)


    def drawSol(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                if self._mat[i][j] != Map.empty :
                    if self.affiche(Coord(j,i)) :
                        if Season.spring(self):
                            canvas.create_image(j * 50, i * 50, anchor=NW, image=textures['map']['sol'])
                        elif Season.summer(self):
                            canvas.create_image(j * 50, i * 50, anchor=NW, image=textures['map']['solSummer'])
                        elif Season.fall(self):
                            canvas.create_image(j * 50, i * 50, anchor=NW, image=textures['map']['solFall'])
                        elif Season.winter(self):
                            canvas.create_image(j * 50, i * 50, anchor=NW, image=textures['map']['solWinter'])
                    else:
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['map']['solFoncé'])
        canvas.pack()
    
    def drawCGround(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                if self._mat[i][j] != Map.empty :
                    if self.affiche(Coord(j,i)) :
                        canvas.create_image(j * 50, i * 50, anchor=NW, image=textures['map']['solC'])
    def affiche(self, coord):
        ### renvoie True si on doit drawr la case
        ###  sinon False
        if self.pos(self.hero).distance(coord) < theGame().hero.dist :
            return True
        return False

    def drawMobs(self):
        if 'Silver Chariot' not in str(Game.copieNext):
            Map.chariot = False
        else:
            Map.chariot = True
        
        if 'WoU' not in str(Game.copieNext):
            Map.WoU = False
        else:
            Map.WoU = True

        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Element):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == "G":
                            canvas.create_image(j * 50,
                                                i * 50,
                                                anchor=NW,
                                                image=textures['mobs']['Gobelin'])
                            # draw rectangle

                        if el.abbrv == "D":
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Doge'])
                        
                        if el.abbrv == "H":
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Harvest'])
                        
                        if el.abbrv == "B":
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Blob'])
                        
                        if el.abbrv == 'Dragon':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Dragon'])
                        
                        if el.abbrv == 'Napstablook':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Napstablook'])

                        if el.abbrv == 'Silver Chariot':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Silver Chariot Requiem'])
                            Map.chariot = True
                        
                        if el.abbrv == 'Regirust':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Regirust'])
                        
                        if el.abbrv == 'Unjoy':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Unjoy'])

                        if el.abbrv == 'WoU' : 
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['WoU'])
                            Map.WoU = True
                        
                        if el.abbrv == 'Sans': ### peut regarder dans les 4 directions en fonction de la position du héro
                            if self.pos(el).direction(self.pos(self.hero)) == Coord(-1,0):
                                canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['sans L'])
                            if self.pos(el).direction(self.pos(self.hero)) == Coord(1,0):
                                canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['sans R'])
                            if self.pos(el).direction(self.pos(self.hero)) == Coord(0,-1):
                                canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['sans U'])
                            if self.pos(el).direction(self.pos(self.hero)) == Coord(0,1):
                                canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['sans D'])
                        
                        if el.abbrv == 'Metallica':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Metallica'])
                        
                        if el.abbrv == 'C-Moon':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['C-Moon'])

                        if el.abbrv == 'Enigma':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Enigma'])
                        
                        if el.abbrv == 'Akaza':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Akaza'])
                        
                        if el.abbrv == 'Slender':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Slender'])
                        
                        if el.abbrv == 'Spider':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Spider'])

                        if el.abbrv == 'Hoopa':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Hoopa'])                  
                        
                        if el.abbrv == 'Merchant' :
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['MerchantIt'])             
                        
                        if el.abbrv == 'MerchantIt' :
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Merchant'])        
                        
                        if el.abbrv == 'Mimic':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Mimic'])
                        
                        if el.abbrv == 'Kecleon':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Kecleon'])
                        
                        if el.abbrv == 'Regimelt':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Regimelt'])
                        
                        if el.abbrv == 'Mettaton':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Mettaton'])

    def drawHero(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Hero):
                    if theGame().hero.invisible != None :
                        if 'Gun' in (str(i) for i in theGame().hero.sword):
                            if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorCowBoyInvisible'])
                            elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorCowBoyInvisible'])
                            else:
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroCBInvisible'])
                        
                        elif 'Bodyguard 638' in (str(i) for i in theGame().hero.sword):
                            if 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorMistaInvisible'])
                            elif 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorMistaInvisible'])
                            else:
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroMistaInvisible'])

                        elif 'Rainbow Sword' in (str(i) for i in theGame().hero.sword):
                            if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorRainbowSwordInvisible'])
                            elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorRainbowSwordInvisible'])
                            else:
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroSwordInvisible'])
                        elif 'Katana' in (str(i) for i in theGame().hero.sword):
                            if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorKatanaInvisible'])
                            elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorKatanaInvisible'])                            
                            else:
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroKatanaInvisible'])

                        elif 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorInvisible'])
                        elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorInvisible'])
                        else:
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroInv'])

                    elif 'Rainbow Sword' in (str(i) for i in theGame().hero.sword):
                        if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorRainbowSword'])
                        elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorRainbowSword'])
                        else:
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroSword'])

                    elif 'Katana' in (str(i) for i in theGame().hero.sword):
                        if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorKatana'])
                        elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorKatana'])
                        else:
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroKatana'])

                    elif 'Gun' in (str(i) for i in theGame().hero.sword):
                        if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorCowBoy'])
                        elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorCowBoy'])
                        else:
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroCB'])
                    elif 'Bodyguard 638' in (str(i) for i in theGame().hero.sword):
                        
                        if 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorMista'])
                        elif 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorMista'])
                        else:
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroMista'])

                    elif 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmor'])
                    
                    elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmor'])
                    else:
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['Hero'])

    
    def drawItems(self):

        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Equipment):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == 'Moonstaff':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Moonstaff'])

                        if el.abbrv == 'TNT':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['TNT'])

                        if el.abbrv == "Potion de vie":
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Health Pot'])

                        if el.abbrv == "Potion d'invisibilité":
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Invisible pot'])
                                                
                        if el.abbrv == 'Dogecoin':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Dogecoin'])

                        if el.abbrv == 'Gun':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Gun'])
                        
                        if el.abbrv == 'Rainbow Sword':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Rainbow Sword'])    

                        if el.abbrv == 'Apple':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Apple'])       

                        if el.abbrv == 'Pizza':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Pizza'])

                        if el.abbrv == 'Katana':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Katana'])
                    
                        if el.abbrv == 'Blue Armor':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Blue Armor'])
                       
                        if el.abbrv == 'Iron Armor':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Iron Armor'])
                        
                        if el.abbrv == 'Chicken':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Chicken'])
                        
                        if el.abbrv == 'Bodyguard 638':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Smith&Wesson'])
                        
                        if el.abbrv == 'MimicIt':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['items']['MimicIt'])

                           

    def drawStairs(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Stairs):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == 'stairs':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['map']['stairs'])
    
    def drawMoney(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Money):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == 'Dogecoin':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Dogecoin'])
    
    def drawKids(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Kids):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == 'Monophanie':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['kids']['Monophanie'])
                        if el.abbrv == 'Monosuke' :
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['kids']['Monosuke'])
                        if el.abbrv == 'Monodam' :
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['kids']['Monodam'])
                        if el.abbrv == 'Monotaro' :
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['kids']['Monotaro'])
                        if el.abbrv == 'Monokid' :
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['kids']['Monokid'])
    
    def drawProjectiles(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, MetallicProjectile):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == 'Bee' :
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Bee'])
    
    def addRoom(self, room):
        """Adds a room in the map."""
        self._roomsToReach.append(room)
        for y in range(room.c1.y, room.c2.y + 1):
            for x in range(room.c1.x, room.c2.x + 1):
                self._mat[y][x] = Map.ground

    def findRoom(self, coord):
        """If the coord belongs to a room, returns the room elsewhere returns None"""
        for r in self._roomsToReach:
            if coord in r:
                return r
        return None

    def intersectNone(self, room):
        """Tests if the room shall intersect any room already in the map."""
        for r in self._roomsToReach:
            if room.intersect(r):
                return False
        return True

    def dig(self, coord):  ### Transforme n'importe quelle case en Ground. Gère les salles atteintes.
        """Puts a ground cell at the given coord.
            If the coord corresponds to a room, considers the room reached."""
        self._mat[coord.y][coord.x] = Map.ground
        r = self.findRoom(coord)
        if r:
            self._roomsToReach.remove(r)
            self._rooms.append(r)

    def corridor(self, cursor, end):
        """Digs a corridors from the coordinates cursor to the end, first vertically, then horizontally."""
        d = end - cursor
        self.dig(cursor)
        while cursor.y != end.y:
            cursor = cursor + Coord(0, sign(d.y))
            self.dig(cursor)
        while cursor.x != end.x:
            cursor = cursor + Coord(sign(d.x), 0)
            self.dig(cursor)

    def reach(self
              ):  ### Prend 2 rooms random et creuse un couloir entre les deux
        """Makes more rooms reachable.
            Start from one random reached room, and dig a corridor to an unreached room."""
        roomA = random.choice(self._rooms)
        roomB = random.choice(self._roomsToReach)

        self.corridor(roomA.center(), roomB.center())

    def reachAllRooms(self):
        """Makes all rooms reachable.
            Start from the first room, repeats @reach until all rooms are reached."""
        self._rooms.append(self._roomsToReach.pop(0))
        while len(self._roomsToReach) > 0:
            self.reach()

    def randRoom(self):  ### return une room aléatoire
        """A random room to be put on the map."""
        c1 = Coord(random.randint(0,
                                  len(self) - 3),
                   random.randint(0,
                                  len(self) - 3))
        c2 = Coord(min(c1.x + random.randint(3, 8),
                       len(self) - 1),
                   min(c1.y + random.randint(3, 8),
                       len(self) - 1))
        return Room(c1, c2)

    def generateRooms(
            self, n
    ):  ### Génère n rooms aléatoires et les ajoute aux salles à atteindre
        """Generates n random rooms and adds them if non-intersecting."""
        for i in range(n):
            r = self.randRoom()
            if self.intersectNone(r):
                self.addRoom(r)
    def randCoordPlus(self,roomSize):  #Retourne une coordonnée aléatoire, dans une certaine zone.
        return Coord(random.randrange(self.size - roomSize.x),
                     random.randrange(self.size - roomSize.y))

    def __len__(self):
        return len(self._mat)

    def __contains__(self, item):
        if isinstance(item, Coord):
            return 0 <= item.x < len(self) and 0 <= item.y < len(self)
        return item in self._elem

    def __repr__(self):
        s = ""
        for i in self._mat:
            for j in i:
                s += str(j)
            s += '\n'
        return s

    def checkCoord(self, c):
        ""r"Check if the coordinates c is valid in the map."""
        if not isinstance(c, Coord):
            raise TypeError('Not a Coord')
        if not c in self:
            raise IndexError('Out of map coord')

    def checkElement(self, o):
        """Check if o is an Element."""
        if not isinstance(o, Element):
            raise TypeError('Not a Element')

    def put(self, c, o):

        self.checkCoord(c)
        self.checkElement(o)
        if self._mat[c.y][c.x] != Map.ground:
            if isinstance(self._mat[c.y][c.x],Stairs):
                return None
            raise ValueError('Incorrect cell')
        if o in self._elem:
            raise KeyError('Already placed')
        self._mat[c.y][c.x] = o
        self._elem[o] = c

    def get(self, c):
        self.checkCoord(c)
        return self._mat[c.y][c.x]

    def pos(self, o):

        self.checkElement(o)
        return self._elem[o]

    def rm(self, c):

        self.checkCoord(c)
        del self._elem[self._mat[c.y][c.x]]
        self._mat[c.y][c.x] = Map.ground

    def move(self, e, way):
        
        orig = self.pos(e)
        dest = orig + way
        if dest in self:
            
            if self.get(dest) == Map.ground:
                if e.on != None :
                        
                    self._mat[e.on[1].y][e.on[1].x] = e.on[0]
                    e.on = None
                else :
                    self._mat[orig.y][orig.x] = Map.ground
                self._mat[dest.y][dest.x] = e
                self._elem[e] = dest
            
            elif e.abbrv == 'WoU':
                if self.get(dest) == Map.empty:
                    self._mat[orig.y][orig.x] = Map.ground
                    self._mat[dest.y][dest.x] = Map.ground
                    self._mat[dest.y][dest.x] = e
                    self._elem[e] = dest

            
            elif (self.get(dest) != Map.empty and 
            isinstance(self.get(dest), Equipment) and 
            len(self.hero._inventory) == 5) or (self.get(dest) != Map.empty and isinstance(self.get(dest), Equipment) and not(isinstance(e,Hero)))and self.get(dest).abbrv !='MerchantIt':
                if e.on != None :
                    self._mat[orig.y][orig.x] = e.on[0]
                    e.on = None
                else :
                    self._mat[orig.y][orig.x] = Map.ground
                        
                e.on = [self._mat[dest.y][dest.x], dest]

                self._mat[dest.y][dest.x] = e
                self._elem[e] = dest
                    

            elif self.get(dest) != Map.empty  and self.get(dest).meet(
                        e) and self.get(dest) != self.hero:

                    if isinstance(self.get(dest), Kids):
                        theGame().l.remove(self.get(dest))
                    if isinstance(self.get(dest), Creature):
                        theGame().hero.kill+=1
                        theGame().hero.addXP(self.get(dest).xp)
                        if self.get(dest).on != None :
                            if len(self.hero._inventory) < 5 :
                                self.hero._inventory.append(self.get(dest).on[0])
                            else :
                                self.hero.on = self.get(dest).on[0]

                    if e.on != None:
                        self._mat[orig.y][orig.x] = e.on[0]
                        e.on = None
                    else:
                        self._mat[orig.y][orig.x] = Map.ground

                    self.rm(dest)
                    self._mat[dest.y][dest.x] = e
                    self._elem[e] = dest

    def moveAllMonsters(
            self
        ):  #### tous les mobs bougent après chaque tour, si un mob est à 1 case du héro sans avoir bougé, le mob attaque le héro.
            h = self.pos(self.hero)
            for e in self._elem:
                c = self.pos(e)
                if isinstance(e,
                            Creature) and e != self.hero and c.distance(h) < 8:
                    d = c.direction(h)
                    if e.abbrv == 'Sans': ### gagne de l'attaque à chaque mob tué
                        e.strength=math.ceil(theGame().hero.kill/2)
                        e.xp = math.ceil(theGame().hero.kill/2)
                    if e.abbrv == 'WoU':
                        if self.get(c+d) in [Map.ground, self.hero, Map.empty] or isinstance(self.get(c+d), Equipment):
                            self.move(e, d)
                    elif self.get(c + d) in [Map.ground, self.hero] or isinstance(self.get(c+d), Equipment) and self.get(c+d).abbrv !='MerchantIt':
                        self.move(e, d)           
                    


def makeInvisible(creature) :
    """Make the hero invisible"""
    if creature == theGame().hero:
        theGame().hero.invisible = 20
    else:
        creature.hp-=10
    return True

def makeVisible(creature) :
    creature.invisible = None

def heal(creature, satiety = 0):
    """Heal the creature"""
    if 'WoU' in str(theGame().floor):
        theGame().addMessage("Can't heal now \n")
        return False
    if 'Silver Chariot' in str(theGame().floor):
        if creature.hp + 15 >= creature.hpMax:
            creature.hp = creature.hpMax
        else:
            creature.hp += 15
        if isinstance(creature, Hero):
            if theGame().hero.hunger+satiety>100:
                theGame().hero.hunger = 100
            else:
                theGame().hero.hunger+=math.ceil(satiety/2)
    else:
        if creature.hp + 30 >= creature.hpMax:
            creature.hp = creature.hpMax
        else:
            creature.hp += 30
        if isinstance(creature, Hero):
            if theGame().hero.hunger+satiety>100:
                theGame().hero.hunger = 100
            else:
                theGame().hero.hunger+=satiety
    return True

def nourrir(creature,qte, name = '') :
    """ You eat food """
    if name == 'Chicken' and 'Silver Chariot' not in str(theGame().floor):
            creature.strength +=1
    if 'Silver Chariot' in str(theGame().floor):
        if isinstance(creature, Hero) :
            if (creature.hunger + math.ceil(qte/2)) > 100 :
                creature.hunger = 100
            else :
                creature.hunger += math.ceil(qte/2)
        else:
            creature.hp+=30
    if not Season.winter(Season) and not Season.summer(Season):
        if isinstance(creature, Hero) :
            if (creature.hunger + qte) > 100 :
                creature.hunger = 100
            else :
                creature.hunger += qte
        else:
            creature.hp+=30
    else:
        if isinstance(creature, Hero) :
            if (creature.hunger + qte + math.ceil(qte/2)) > 100 :
                creature.hunger = 100
            else :
                creature.hunger += qte + math.ceil(qte/2)
        else:
            creature.hp+=30
    return True

def teleport(creature, unique):
    """Teleport the creature"""
    r = theGame().floor.randRoom()
    c = r.randCoord()
    while not theGame().floor.get(c) == Map.ground:
        c = r.randCoord()
    theGame().floor.rm(theGame().floor.pos(creature))
    theGame().floor.put(c, creature)
    theGame().addEffect('You used Teleport ! \n')
    return unique


def equip(creature,attack):
    """ You equip a weapon """
    if creature == theGame().hero:
        theGame().hero.equipped = True 
        if len(theGame().hero.sword) == 0:
            theGame().hero.strength+=attack
        
        elif len(theGame().hero.sword) != 0 and len(theGame().hero._inventory) < 5:
            theGame().hero.strength-=theGame().hero.sword[0].attack
            theGame().hero.strength+=attack
            theGame().hero._inventory.append(theGame().hero.sword[0])
            theGame().hero.sword.remove(theGame().hero.sword[0])
        
        elif len(theGame().hero.sword) != 0 and len(theGame().hero._inventory) >=5:

            theGame().hero.sword.remove(theGame().hero.sword[0])

    
    else:
        creature.hp-=50
        if creature.hp<0:
            theGame().hero.addXP(theGame().floor.get(theGame().floor.pos(creature)).xp)
            theGame().floor.rm(theGame().floor.pos(creature))
    return True

def equipArmor(creature, armor):
    """ You equip an Armor"""
    if creature == theGame().hero:
        theGame().hero.armored = True
        if len(theGame().hero.armor) == 0:
            if Season.summer(Season):
                theGame().hero.protection+=armor-5
            elif Season.winter(Season):
                theGame().hero.protection+=armor+5
            else:
                theGame().hero.protection+=armor
 
        elif len(theGame().hero.armor) != 0 and len(theGame().hero._inventory) < 5:
            theGame().hero._inventory.append(theGame().hero.armor[0])
            theGame().hero.armor.remove(theGame().hero.armor[0])

        elif len(theGame().hero.sword) != 0 and len(theGame().hero._inventory) >=5:
            theGame().hero.armor.remove(theGame().hero.armor[0]) 
    
    else:
        creature.hp-=50
        if creature.hp<0:
            theGame().hero.addXP(theGame().floor.get(theGame().floor.pos(creature)).xp)
            theGame().floor.rm(theGame().floor.pos(creature))
    return True 

def throw(creature,dmg, name = ''):
    """ You throw an item"""
    if isinstance(creature, Hero):
        theGame().addMessage("You can't use the " + name + '\n')
        return False
    if name == 'TNT':
        creature.hp-=dmg+30
    else:
        creature.hp-=dmg
    if creature.hp<0:
        theGame().hero.addXP(theGame().floor.get(theGame().floor.pos(creature)).xp)
        theGame().floor.rm(theGame().floor.pos(creature))

    return True

class Game(object):
    """ Class representing game state """

    copieNext = ''
    equipments = {0: [Food("Health pot", "Potion de vie", usage=lambda self, creature: heal(creature,20)),
                      Food("Invisible pot", "Potion d'invisibilité", usage=lambda self, creature: makeInvisible(creature)),
                      MetallicProjectile("Bee Gees", "Bee"),
                      Food("Apple", "Apple", usage=lambda self, creature: nourrir(creature, 30)),
                      Armor('Iron Armor', 'Iron Armor', usage = lambda self, creature : equipArmor(creature,10)) ], \
                  1: [
                      Metal('Gun', 'Gun', attack = 0,usage =lambda self, creature : equip(creature, 0)),

                      Food('Pizza', 'Pizza', usage=lambda self, creature: nourrir(creature, 50)),
                      Sword("Catch the Rainbow", abbrv = "Rainbow Sword", attack = 12, usage =lambda self, creature : equip(creature,12)),
                      Sword('Katana', 'Katana', attack = 10, usage =lambda self, creature : equip(creature,10)),
                      Food("Invisible pot", "Potion d'invisibilité", usage=lambda self, creature: makeInvisible(creature)),
                       ], \
                  2: [
                      Equipment('TNT','TNT', usage =lambda self, creature : throw(creature,70, name = 'TNT'))  ], \
                  3: [
                      Equipment("Moonstaff", "Moonstaff", usage =lambda self, creature : teleport(creature, True)),
                      Armor('Blue Armor', 'Blue Armor', usage = lambda self, creature : equipArmor(creature,12)) ],
                  7: [Food('The Chicken', 'Chicken', usage = lambda self, creature : nourrir(creature, 75, name = 'Chicken')),
                    Metal('Bodyguard 638', 'Bodyguard 638', attack = 0, usage = lambda self, creature : equip(creature,0))]
                  }
    mimicLoot = {0: [
                      Equipment("Moonstaff", "Moonstaff", usage =lambda self, creature : teleport(creature, True)),
                      Armor('Blue Armor', 'Blue Armor', usage = lambda self, creature : equipArmor(creature,18)) ],
                 2: [Food('The Chicken', 'Chicken', usage = lambda self, creature : nourrir(creature, 80, name = 'Chicken')),
                    Metal('Bodyguard 638', 'Bodyguard 638', attack = 5, usage = lambda self, creature : equip(creature,5))]

    }

    shopInv = {0: [
                      Metal('Gun', 'Gun', attack = 2,usage =lambda self, creature : equip(creature, 2),nonShop=False,price=7),
                      Food('Pizza', 'Pizza', usage=lambda self, creature: nourrir(creature, 50),nonShop=False,price=8),
                      Sword("Catch the Rainbow", abbrv = "Rainbow Sword", attack = 17, usage =lambda self, creature : equip(creature,17),nonShop=False,price=13),
                      Sword('Katana', 'Katana', attack = 15, usage =lambda self, creature : equip(creature,15),nonShop=False,price=12),
                                           Food("Apple", "Apple", usage=lambda self, creature: nourrir(creature, 30),nonShop=False,price=5)], \
                  1: [
                      Equipment('TNT','TNT', usage =lambda self, creature : throw(creature,70),nonShop=False,price=13)  ], \
                  2: [
                      Equipment("Moonstaff", "Moonstaff", usage =lambda self, creature : teleport(creature,True),nonShop=False,price=15),
                      Armor('Blue Armor', 'Blue Armor', usage = lambda self, creature : equipArmor(creature,17),nonShop=False,price=15),
                      Food('The Chicken', 'Chicken', usage = lambda self, creature : nourrir(creature, 85, name = 'Chicken'),nonShop=False,price=13) ]}


    munitions = {0 :[MetallicProjectile("Bee Gees", "Bee"),
                    MetallicProjectile("Bee Gees", "Bee"),
                    MetallicProjectile("Bee Gees", "Bee"),
                    MetallicProjectile("Bee Gees", "Bee"),
                    MetallicProjectile("Bee Gees", "Bee"),
                    MetallicProjectile("Bee Gees", "Bee"),
                 ]
}
    """ available monsters """
    monsters = {
        0: [
            Creature("Goblin", 4, xp=1),
            Creature("Napstablook", 2, abbrv ='Napstablook', xp=1),
            Creature("Harvest", 2, xp=1),
            Creature("Doge",4, xp=1),
            Creature('C-Moon', 30, abbrv = 'C-Moon', strength = 20, xp = 35),
            Creature('C-Moon', 30, abbrv = 'C-Moon', strength = 20, xp = 35),
            Creature('C-Moon', 30, abbrv = 'C-Moon', strength = 20, xp = 35)],

        1: [Creature("Blob", 10,xp=2),],

        6: [Creature("Dragon", 8, abbrv = 'Dragon', strength=3, xp=4)],
        
        8: [Creature('Regirust', 50, abbrv='Regirust', strength = 7, xp=5)],

        9:[Creature('Silver Chariot', 55, strength = 8, abbrv = 'Silver Chariot', xp = 30)],
        
        10:[Creature('Wonder Of U', 60, abbrv = 'WoU', strength=10, xp = 40),
            Creature('Unjoy',40,abbrv ='Unjoy', strength=7, xp=50),
            Creature('Metallica', 3, abbrv = 'Metallica', strength=3, xp=1),
            Creature('C-Moon', 30, abbrv = 'C-Moon', strength = 20, xp = 35)],
        
        17:[Creature('Sans', 1, abbrv = 'Sans', strength=1, xp=3)]
    }
    Cmonsters = {
        0: [
            Creature("Enigma", 30, abbrv = 'Enigma', strength = 10, xp=0),
            Creature("Akaza", 50, abbrv = 'Akaza', strength = 15, xp=0),
            Creature("Slender", 20, abbrv = 'Slender', strength = 13, xp=0),
            Creature("Spider", 25, abbrv = 'Spider', strength = 5, xp=0),
            Creature('Hoopa', 50, abbrv = 'Hoopa', strength= 16, xp=0)]}
    
    hoopaMonsters = {
        0: [Creature('Silver Chariot', 18, strength = 4, abbrv = 'Silver Chariot', xp = 0),
            Creature("Goblin", 4, xp=0),
            Creature("Regimelt", 95, abbrv = 'Regimelt', strength = 14, xp=0),
            Creature("Kecleon", 110, abbrv = 'Kecleon', strength = 10, xp=0),
            Creature('Wonder Of U', 30, abbrv = 'WoU', strength=6, xp = 0),
            Creature('Metallica', 1, abbrv = 'Metallica', strength=3, xp=0),
            Creature('Mettaton', 130, abbrv = 'Mettaton', strength=7, xp=0)]}
    """Escaliers"""
    element = {
        0:
        
            Stairs('Stairs', 'stairs'),
        
    
    }

    """Monnaie"""
    money = {0:
        [Money('Dogecoin', 'Dogecoin', value = 1)]
        
        }
    """ available actions """
    _actions = {'z': lambda h: theGame().floor.move(h, Coord(0, -1)), \
                'q': lambda h: theGame().floor.move(h, Coord(-1, 0)), \
                's': lambda h: theGame().floor.move(h, Coord(0, 1)), \
                'd': lambda h: theGame().floor.move(h, Coord(1, 0)), \
                ' ': lambda h: None, \
                'c': lambda hero: theGame().hero._inventory.remove(theGame().hero._inventory[theGame().select]),
                '&': lambda hero: theGame().hero.use(theGame().hero._inventory[theGame().select]),\
                "x": lambda hero: theGame().hero.unequipped(),
                "w": lambda hero: theGame().hero.unequippedArmor(),
       
                }

    def __init__(self, level=1, hero=None):
        self.thief=False
        self.steal=0
        self.level = level
        self._message = []
        self.effect = []
        if hero is None:
            hero = Hero()
        self.posInventaire=0
        self.hero = hero
        self.floor = None
        self.hero.hp = 70
        self.hero.hpMax = 70
        self.bonus=0
        self.select = 0
        self.Monokid =  Kids("Monokid","Monokid")
        self.Monosuke = Kids("Monosuke", "Monosuke")
        self.Monotaro = Kids("Monotaro", "Monotaro")
        self.Monophanie = Kids("Monophanie", "Monophanie")
        self.Monodam = Kids ("Monodam", "Monodam")
        self.hunger = 100
        self.calamitycpt = 0
        self.transform = 0
        
        self.l = [self.Monosuke,self.Monophanie,self.Monotaro,self.Monodam,self.Monokid]

    def buildFloor(self):  ### initialise le floor à une nouvelle map
        self.floor = Map(hero=self.hero)
    
    def newFloor(self):  ### Nouvel étage
        if self.thief is False:
            self.steal=0
        self.bonus+=1
        if Season.fall(Season):
            self.transform=10
        else:
            self.transform = 0
        canvas.delete('all')
        if self.floor.chariot is True: 
            present = True
        else:            
            present = False

        if self.floor.WoU is True:
            presentWoU = True
        else:
            presentWoU = False
        
        if self.hero.hp+30>self.hero.hpMax:   
            self.hero.hp=self.hero.hpMax
        else:
            self.hero.hp+=30
        
        self.level+=1
        self.buildFloor()
        
        if 'stairs' not in str(self.floor):
            randomRoom = random.randint(1, len(self.floor._mat))
            self.floor._mat[self.floor._rooms[randomRoom].center().y][self.floor._rooms[randomRoom].center().x] = 'stairs'
        
        self.floor._mat[self.floor._rooms[0].center().y][self.floor._rooms[0].center().x] = Map.ground
        self.floor.put(self.floor._rooms[0].center(), self.hero)
        self.putRandomKids()

        Game.copieNext = copy.deepcopy(theGame().floor) ### inchangeable copie de la map non modifiée

        self.drawTout()
        if 'WoU' not in str(self.copieNext):
            if 'Silver Chariot' in str(self.copieNext) and present == False:   #### si chariot dans la salle et chariot mort de la salle précédente
                winsound.PlaySound(r"./musique jeu/chariot.wav", winsound.SND_ASYNC)
                        

                                        ### si chariot n'est pas dans la salle et chariot mort dans la salle précédente    
            elif 'Silver Chariot' not in str(self.copieNext) and present == True:
                winsound.PlaySound(r"./musique jeu/ClosingArgumentDGS.wav", winsound.SND_ASYNC)
            
            elif  'Silver Chariot' not in str(self.copieNext) and presentWoU is True:
                winsound.PlaySound(r"./musique jeu/ClosingArgumentDGS.wav", winsound.SND_ASYNC)                
        
        
        if 'WoU' in str(self.copieNext) and presentWoU is False:
                winsound.PlaySound(r"./musique jeu/WoU.wav", winsound.SND_ASYNC)

    def cFloor(self):
        self.hero.otherDim = True
        self.buildFloor()
        self.addEffect('You traveled through dimensions ! \n')

        #playsound(r"./musique jeu/dimension.wav")

        if 'stairs' not in str(self.floor):
            randomRoom = random.randint(1, len(self.floor._mat))
            self.floor._mat[self.floor._rooms[randomRoom].center().y][self.floor._rooms[randomRoom].center().x] = 'stairs'
        
        self.floor._mat[self.floor._rooms[0].center().y][self.floor._rooms[0].center().x] = Map.ground
        self.floor.put(self.floor._rooms[0].center(), self.hero)
        window.bind('<KeyPress>', self.mainGame)

        return True
    
    def addMessage(self, msg):  #### ajoute un message à la liste de messages

        self._message.append(msg)

    def addEffect(self, msg):
        self.effect.append(msg)

    def readMessages(
            self):  #### lis les messages et clear la liste de messages

        s = ''
        for m in self._message:
            s += m
        self._message.clear()
        canvasInventaire.create_text(700,300, text = s, font= 'Arial 13 ', fill = 'red')
    
    def readEffect(self): ### lis les effets des mobs
        s = ''
        for m in self.effect:
            s+=m
        self.effect.clear()
        canvasInventaire.create_text(450,500, text = s, font = 'Arial 15', fill = 'turquoise')

    def randElement(self, collect):  #### génère un élément aléatoire
        """Returns a clone of random element from a collection using exponential random law."""
        x = random.expovariate(1 / self.level)
        for k in collect.keys():
            if k <= x:
                l = collect[k]
        a = copy.copy(random.choice(l))
        
        if isinstance(a, Creature):
            a.strength += self.bonus
            if a.abbrv == 'Sans': 
                a.hp+=self.bonus+self.hero.kill
            else:
                a.hp+=self.bonus
            a.xp+=self.bonus/2

        return a
    
    def randEquipment(self):  #### génère un équipement aléatore

        return self.randElement(Game.equipments)
    def randShopItem(self):  #### génère un équipement non prenable aléatore

        return self.randElement(Game.shopInv)
    
    def randMimicLoot(self):

        return self.randElement(Game.mimicLoot)
    
    def randHoopa(self):
        
        return self.randElement(Game.hoopaMonsters) 
    
    def randMonster(self):  #### génère un mob aléatoire
            
        return self.randElement(Game.monsters)
    
    def randCMonster(self):

        return self.randElement(Game.Cmonsters)
    
    def randMoney(self):

        return self.randElement(Game.money)
    def randAmmo(self):
        
        return self.randElement(Game.munitions)

    def putRandomKids(self): ### put des kids dans la map
        if self.l == []:
            self.l = [self.Monosuke,self.Monophanie,self.Monotaro,self.Monodam,self.Monokid]
        rng = random.randint(0,10)
        if (rng == 1 or rng == 6 or rng == 2) and self.Monosuke in self.l and self.Monosuke not in self.hero._bag:
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monosuke)

        if (rng == 2 or rng == 7 or rng == 3) and self.Monophanie in self.l and self.Monophanie not in self.hero._bag:          
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monophanie)

        if (rng == 3 or rng == 8 or rng == 4) and self.Monotaro in self.l and self.Monotaro not in self.hero._bag :
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monotaro)

        if (rng == 4 or rng == 9 or rng == 5) and self.Monodam in self.l and self.Monodam not in self.hero._bag:
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monodam)

        if (rng == 5 or rng == 10 or rng == 6) and self.Monokid in self.l and self.Monokid not in self.hero._bag:
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monokid)
        
    
    def drawKidsInterface(self):
        for i in self.hero._bag:
            if str(i) == 'Monosuke':
                canvasInventaire.create_image(600,600, anchor = NW, image = textures['kids']['Monosuke'])
            if str(i) == 'Monophanie':
                canvasInventaire.create_image(480,600, anchor = NW, image = textures['kids']['Monophanie'])
            if str(i) == 'Monotaro':
                canvasInventaire.create_image(360,590, anchor = NW, image = textures['kids']['Monotaro'])
            if str(i) == 'Monodam':
                canvasInventaire.create_image(240,600, anchor = NW, image = textures['kids']['Monodam'])
            if str(i) == 'Monokid':
                canvasInventaire.create_image(120,600, anchor = NW, image = textures['kids']['Monokid'])
    
    def calamity(self): 
        """Wonder Of U ability"""
        if 'WoU' in str(self.floor):
            if self.level < 10:
                self.calamitycpt+=1
            elif 10<=self.level<13 :
                self.calamitycpt+=2
            elif self.level>=13:
                self.calamitycpt+=3
            if self.calamitycpt>=15:
                self.calamitycpt = 0
                if len(self.hero._inventory)>0:
                    self.hero._inventory.remove(self.hero._inventory[0])
            self.hero.sick = True
            canvasInventaire.create_image(430,280, anchor = NW, image = textures['interface']['WoU'])
            self.hero.starve=8
            return True        
        self.hero.starve=2
        return False
    
    
    ############################################################### Throw all directions ######
    def throwUP(self,event):
        a = theGame().floor.pos(self.hero)
        b = copy.deepcopy(a)
            
        try:
            while theGame().floor.get(Coord(b.x,b.y-1))!=Map.empty:
                b.y-=1
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Creature) and theGame().floor.get(Coord(b.x,b.y))!=self.hero: ### si objet rencontre creature
                    creature = True
                    break
                creature = False
        except IndexError:
            b.y = 0
            creature = False
        
        if ('Gun' not in (str(i) for i in self.hero.sword) and 'Bodyguard 638' not in (str(i) for i in self.hero.sword)) or 'Bee' not in (str(j) for j in self.hero._stock):
            if len(self.hero._inventory) == 0:
                theGame().addMessage("Empty inventory, can't throw \n")
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.drawTout()
                return False
            if creature is False:
                    
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Equipment) or isinstance(theGame().floor.get(Coord(b.x,b.y)), Money):
                    theGame().floor.rm(Coord(b.x,b.y))
                    
                elif isinstance(theGame().floor.get(Coord(b.x,b.y)),Kids):
                    self.hero._inventory.remove(self.hero._inventory[self.select])
                

                theGame().floor.put(Coord(b.x,b.y), self.hero._inventory[self.select])
            else:
                theGame().floor.get(Coord(b.x,b.y)).use(self.hero._inventory[self.select])
            self.hero._inventory.remove(self.hero._inventory[self.select])

        else:
            for i in self.hero._stock:
                if str(i) == 'Bee':
                    self.hero._stock.remove(i)
                    #playsound(r'musique jeu\Gunshot.wav')
                    if creature is True:
                        MetallicProjectile.setdmg(self)
                        theGame().floor.get(Coord(b.x,b.y)).hp-=i.dmg
                        if theGame().floor.get(Coord(b.x,b.y)).hp<0:
                            self.hero.kill+=1
                            self.hero.addXP(theGame().floor.get(Coord(b.x,b.y)).xp)
                            theGame().floor.rm(theGame().floor.pos(theGame().floor.get(Coord(b.x,b.y))))
                    break

        
        canvasInventaire.delete('all')
        canvas.delete('all')
        self.floor.moveAllMonsters()
        self.drawTout()
        

    def throwDown(self,event): 
        a = theGame().floor.pos(self.hero)
        b = copy.deepcopy(a)      
        try:
            while theGame().floor.get(Coord(b.x,b.y+1))!=Map.empty:
                b.y+=1
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Creature) and theGame().floor.get(Coord(b.x,b.y))!=self.hero: ### si objet rencontre creature
                    creature = True
                    break
                creature = False
        except IndexError:
            b.y = theGame().floor.size-1
            creature = False
        
        if ('Gun' not in (str(i) for i in self.hero.sword) and 'Bodyguard 638' not in (str(i) for i in self.hero.sword)) or 'Bee' not in (str(j) for j in self.hero._stock):
            if len(self.hero._inventory) == 0:
                theGame().addMessage("Empty inventory, can't throw \n")
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.drawTout()
                return False
            if creature is False:
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Equipment) or isinstance(theGame().floor.get(Coord(b.x,b.y)), Money):
                    theGame().floor.rm(Coord(b.x,b.y))
                
                elif isinstance(theGame().floor.get(Coord(b.x,b.y)),Kids):
                    self.hero._inventory.remove(self.hero._inventory[self.select])

                theGame().floor.put(Coord(b.x,b.y), self.hero._inventory[self.select])
            
            else:
                theGame().floor.get(Coord(b.x,b.y)).use(self.hero._inventory[self.select])
        
            self.hero._inventory.remove(self.hero._inventory[self.select])
        else:
            for i in self.hero._stock:
                if str(i) == 'Bee':
                    self.hero._stock.remove(i)
                    #playsound(r'musique jeu\Gunshot.wav')
                    if creature is True:
                        MetallicProjectile.setdmg(self)
                        theGame().floor.get(Coord(b.x,b.y)).hp-=i.dmg
                        if theGame().floor.get(Coord(b.x,b.y)).hp<0:
                            self.hero.kill+=1
                            self.hero.addXP(theGame().floor.get(Coord(b.x,b.y)).xp)
                            theGame().floor.rm(theGame().floor.pos(theGame().floor.get(Coord(b.x,b.y))))

                    break

        canvasInventaire.delete('all')
        canvas.delete('all')
        self.floor.moveAllMonsters()

        self.drawTout()
    
    def throwRight(self,event): 
        a = theGame().floor.pos(self.hero)
        b = copy.deepcopy(a)
        try:
            while theGame().floor.get(Coord(b.x+1,b.y))!=Map.empty:
                b.x+=1
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Creature) and theGame().floor.get(Coord(b.x,b.y))!=self.hero: ### si objet rencontre creature
                    creature = True
                    break
                creature = False               
        except IndexError:
            b.x = theGame().floor.size-1
            creature = False
        
        if ('Gun' not in (str(i) for i in self.hero.sword) and 'Bodyguard 638' not in (str(i) for i in self.hero.sword)) or 'Bee' not in (str(j) for j in self.hero._stock):
            if len(self.hero._inventory) == 0:
                theGame().addMessage("Empty inventory, can't throw \n")
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.drawTout()
                return False
            if creature is False:
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Equipment) or isinstance(theGame().floor.get(Coord(b.x,b.y)), Money):
                    theGame().floor.rm(Coord(b.x,b.y))
                
                elif isinstance(theGame().floor.get(Coord(b.x,b.y)),Kids):
                    self.hero._inventory.remove(self.hero._inventory[self.select])

                theGame().floor.put(Coord(b.x,b.y), self.hero._inventory[self.select])
            
            else:
                theGame().floor.get(Coord(b.x,b.y)).use(self.hero._inventory[self.select])
        
            self.hero._inventory.remove(self.hero._inventory[self.select])
        
        else:
            for i in self.hero._stock:
                if str(i) == 'Bee':
                    self.hero._stock.remove(i)
                    #playsound(r'musique jeu\Gunshot.wav')
                    if creature is True:
                        MetallicProjectile.setdmg(self)
                        theGame().floor.get(Coord(b.x,b.y)).hp-=i.dmg
                        if theGame().floor.get(Coord(b.x,b.y)).hp<0:
                            self.hero.kill+=1
                            self.hero.addXP(theGame().floor.get(Coord(b.x,b.y)).xp)
                            theGame().floor.rm(theGame().floor.pos(theGame().floor.get(Coord(b.x,b.y))))                   
                    break
                    
        canvasInventaire.delete('all')
        canvas.delete('all')
        self.floor.moveAllMonsters()
        self.drawTout()
    
    def throwLeft(self,event): 
        a = theGame().floor.pos(self.hero)
        b = copy.deepcopy(a)

        try:
            while theGame().floor.get(Coord(b.x-1,b.y))!=Map.empty:
                b.x-=1
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Creature) and theGame().floor.get(Coord(b.x,b.y))!=self.hero: ### si objet rencontre creature
                    creature = True
                    break
                creature = False                
        except IndexError:
            b.x = theGame().floor.size-1
            creature = False
        
        if ('Gun' not in (str(i) for i in self.hero.sword) and 'Bodyguard 638' not in (str(i) for i in self.hero.sword)) or 'Bee' not in (str(j) for j in self.hero._stock):
            if len(self.hero._inventory) == 0:
                theGame().addMessage("Empty inventory, can't throw \n" )
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.drawTout()
                return False
            
            if creature is False:
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Equipment) or isinstance(theGame().floor.get(Coord(b.x,b.y)), Money):
                    theGame().floor.rm(Coord(b.x,b.y))
                
                elif isinstance(theGame().floor.get(Coord(b.x,b.y)),Kids):
                    self.hero._inventory.remove(self.hero._inventory[self.select])

                theGame().floor.put(Coord(b.x,b.y), self.hero._inventory[self.select])

            else:
                theGame().floor.get(Coord(b.x,b.y)).use(self.hero._inventory[self.select])
            
            self.hero._inventory.remove(self.hero._inventory[self.select])
        else:
            for i in self.hero._stock:
                if str(i) == 'Bee':
                    self.hero._stock.remove(i)
                    #playsound(r'musique jeu\Gunshot.wav')
                    if creature is True:
                        MetallicProjectile.setdmg(self)
                        theGame().floor.get(Coord(b.x,b.y)).hp-=i.dmg
                        if theGame().floor.get(Coord(b.x,b.y)).hp<0:
                            self.hero.kill+=1
                            self.hero.addXP(theGame().floor.get(Coord(b.x,b.y)).xp)
                            theGame().floor.rm(theGame().floor.pos(theGame().floor.get(Coord(b.x,b.y))))
                    break
 
        canvasInventaire.delete('all')
        canvas.delete('all')
        self.floor.moveAllMonsters()
        self.drawTout()

    def drawVie(self):
        l=50
        if self.calamity() or self.hero.sick is True:
            canvasInventaire.create_image(350,300,anchor = NW, image = textures['interface']['viePSN'])
            canvasInventaire.create_text(390,400, text = 'You are sick', font = 'Arial 14', fill = "green")

        else:
            canvasInventaire.create_image(350,300,anchor = NW, image = textures['interface']['vie'])
        
        canvasInventaire.create_rectangle(115,905,815,875, fill ='black')
        if self.hero.hunger>50:
            canvasInventaire.create_rectangle(115,905,100+715*(self.hero.hunger/100),875, fill ='green')
        elif 25<=self.hero.hunger<=50:
            canvasInventaire.create_rectangle(115,905,100+715*(self.hero.hunger/100),875, fill ='orange')
        elif self.hero.hunger<25:
            canvasInventaire.create_rectangle(115,905,100+715*(self.hero.hunger/100),875, fill ='red')
            if self.hero.hunger == 0:
                canvasInventaire.create_text(470,890, text = 'Vous perdez des hp', font = 'Arial 20', fill = 'cyan')
        
        canvasInventaire.create_text(390,336, text = str(self.hero.hp), font = 'Arial 20')
        canvasInventaire.create_image(60,850, anchor = NW, image = textures['interface']['Apple'] )

    def drawTout(self):
        if self.hero.otherDim is False:
            self.floor.drawSol()
        else:
            self.floor.drawCGround()
        self.floor.drawStairs()
        self.floor.drawMobs()
        self.floor.drawKids()
        self.floor.drawItems()
        self.floor.drawProjectiles()
        self.floor.drawHero()
        self.floor.drawMoney()
        self.hero.drawInventaire()
        MetallicProjectile.drawProjectilesInventaire(MetallicProjectile)
        Sword.drawEquippedSword(Sword)
        Armor.drawEquippedArmor(Armor)
        Season.drawSeason(Season)
        Money.showMoney(Money)
        self.drawVie()
        self.hero.drawXp()
        self.drawKidsInterface()
        self.readMessages()
        self.readEffect()
    
    def stillAlive(self):
        if self.hero.hp > 0:
            return True
        else : 
            self.gameOver()
    
    def spawn(self):
        """Transform all Equipements into monsters"""
        once = False
        if 'Unjoy' in str(self.floor):
            self.transform+=1
            if self.transform%17==0:
                for i in range (len(self.floor._mat)):
                    for j in range (len(self.floor._mat[i])):
                        item=self.floor._mat[i][j]
                        if (isinstance(item, Equipment) or isinstance(item, MetallicProjectile)) and item.nonShop is True:
                            a=self.floor.pos(item)
                            self.floor.rm(self.floor.pos(item))
                            self.floor.put(a,self.randMonster())
                            once = True
                            window.unbind('<KeyPress>')

                #if once:
                    #playsound(r'musique jeu\Unjoy.wav')

                self.addEffect('All Equipments on the ground have been transformed into monsters !\n')



    def hoopaSpawn(self):
        """Spawn monsters from Hoopa's ability"""
        if self.hero.otherDim:
            if 'Hoopa' in str(self.floor):
                rng = random.randint(1,20)
                if rng == 2:
                    self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.randHoopa())
                    self.addEffect('Hoopa transported a monster into this dimension !\n')

    def mainGame(self, event): ### méthode principale pour jouer
        event = event.char
        
        if self.level < 7:
            Season.spring(Season)
        elif 7<=self.level<15:
            Season.summer(Season)
        elif 15<=self.level<23:
            Season.fall(Season)
        elif self.level>=23:
            Season.winter(Season)
        
        if self.stillAlive():
            if event in Game._actions:
                Game._actions[event](self.hero)
                if self.hero.invisible is None :
                    if self.hero.meetStairs is False:
                        self.floor.moveAllMonsters()
                    else:
                        self.hero.meetStairs = False          
                else :
                    self.hero.invisible -= 1
                    if self.hero.invisible <= 0 :
                
                        self.hero.invisible = None 
                ### status
                self.hero.faim+=1
                if self.hero.faim%3==0:
                    if self.hero.hunger-self.hero.starve<0:
                        self.hero.hunger = 0
                        self.hero.hp -=1
                    else:
                        self.hero.hunger-=self.hero.starve
                
                if self.hero.sick is True:
                    self.hero.sickness+=1
                    if self.hero.sickness%3==0:
                        self.hero.hp-=1
                
                #### mob abilties
                
                self.spawn()
                self.hoopaSpawn() 
                
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.drawTout()

                window.update()
                window.bind('<KeyPress>',theGame().mainGame)


#### Se déplacer dans l'inventaire

    def goUp(self,event):
        canvasSelect.delete('all')
        if self.posInventaire-100 <0 :
            canvasSelect.create_image(0,0, anchor= NW, image = textures['interface']['select'])
            self.posInventaire=0

        else:
            canvasSelect.create_image(0,self.posInventaire-100, anchor= NW, image = textures['interface']['select'])
            self.posInventaire-=100
        
        if self.select-1<0:
            self.select = 0
        else:
            self.select-=1
         
    def goDown(self,event):
        canvasSelect.delete('all')
        if self.posInventaire+100>400:
            canvasSelect.create_image(0,400, anchor= NW, image = textures['interface']['select'])
            self.posInventaire=400
        else:
            canvasSelect.create_image(0,self.posInventaire+100, anchor= NW, image = textures['interface']['select'])
            self.posInventaire+=100
        
        if self.select >= 4:
            self.select = 4
        else:    
            self.select += 1

    def play(self):
        """1er étage"""
        canvasSelect.focus_set()
        canvasSelect.create_image(0,0, anchor= NW, image = textures['interface']['select'])

        canvasSelect.bind('<Up>', self.goUp)
        canvasSelect.bind('<Down>', self.goDown)
        self.buildFloor()

        if self.floor.get(self.floor._rooms[0].center()) !=Map.ground:
            self.floor._mat[self.floor._rooms[0].center().y][self.floor._rooms[0].center().x]=Map.ground
        self.floor.put(self.floor._rooms[0].center(), self.hero)
        self.putRandomKids()
        self.drawTout()
        self.floor.chariot = False
        winsound.PlaySound(r"musique jeu\ClosingArgumentDGS.wav", winsound.SND_ASYNC)
        window.bind('<Alt-KeyPress-z>', self.throwUP)
        window.bind('<Alt-KeyPress-s>', self.throwDown)
        window.bind('<Alt-KeyPress-d>', self.throwRight)
        window.bind('<Alt-KeyPress-q>', self.throwLeft)
        window.bind('<Any-KeyPress>',self.mainGame)
        self.floor.moveAllMonsters()
    
    def continuer(self,event):
        self.mainGame
    
    def gameOver(self):
        winsound.PlaySound(None, winsound.SND_PURGE)
        canvas.delete('all')
        canvasInventaire.destroy()
        canvasSelect.destroy()
        canvas.create_text(w/2,200, text = 'Game Over', font = 'Arial 70 bold', fill = 'white')


def theGame(game=Game()):
    """Game singleton"""
    return game
    


window = Tk()
window.state("zoomed")

w, h = window.winfo_screenwidth(), window.winfo_screenheight()
debut = Label(text='Bienvenue dans le Rogue', font=('Arial 20'))
canvas = Canvas(window, width=w, height=h, bg='black')
gameOver= Label(canvas, text='Game over', font=('Arial 20'))

canvasInventaire = Canvas(window, width = w, height = h, bg = '#4C4C4C')
canvasInventaire.place(relx=0.56, rely=0)

canvasSelect = Canvas(window, width = 30, height= 438, bg = 'red' )
canvasSelect.place(relx = 0.59, rely = 0.05)



textures = {
    'map': {
        'murs': ImageTk.PhotoImage(Image.open(r"images jeu/wall.png")),
        'sol': ImageTk.PhotoImage(Image.open(r"images jeu\path.png")),
        'solSummer' :ImageTk.PhotoImage(Image.open(r"images jeu\pathSummer.png")),
        'solFall' :ImageTk.PhotoImage(Image.open(r"images jeu\pathFall.png")),
        'solWinter' :ImageTk.PhotoImage(Image.open(r"images jeu\pathSnow.png")),
        'solC' : ImageTk.PhotoImage(Image.open(r"images jeu\pathC2.png")),
        'solFoncé': ImageTk.PhotoImage(Image.open(r"images jeu\path_black.png")),
        'stairs' : ImageTk.PhotoImage(Image.open(r"images jeu\stairs.png"))
    },
    'mobs': {
        'Harvest': ImageTk.PhotoImage(Image.open(r"images jeu\harvest.png")), #à redim + trans
        'Gobelin': ImageTk.PhotoImage(Image.open(r"images jeu\gobelin (1).png")),
        'Doge': ImageTk.PhotoImage(Image.open(r"images jeu\doge.png")), # à redim + trans
        'Blob' : ImageTk.PhotoImage(Image.open(r"images jeu\blob.png")),# à redim + trans
        'Dragon' : ImageTk.PhotoImage(Image.open(r"images jeu\Dragon.png")),
        'Napstablook' : ImageTk.PhotoImage(Image.open(r"images jeu\napstablook.png")),
        'Silver Chariot Requiem' : ImageTk.PhotoImage(Image.open(r"images jeu\SilverChariotRequiem.png")),
        'Regirust' : ImageTk.PhotoImage(Image.open(r"images jeu\regirust.png")),
        'Unjoy' : ImageTk.PhotoImage(Image.open(r"images jeu\unjoy.png")),
        'WoU' : ImageTk.PhotoImage(Image.open(r"images jeu\WonderOfU.png")),
        'sans L' : ImageTk.PhotoImage(Image.open(r"images jeu\killer sans.png")),
        'sans R' : ImageTk.PhotoImage(Image.open(r"images jeu\killer sans2.png")),
        'sans U' : ImageTk.PhotoImage(Image.open(r"images jeu\killer sansUP.png")),
        'sans D' : ImageTk.PhotoImage(Image.open(r"images jeu\killer sansdown.png")),
        'Metallica' : ImageTk.PhotoImage(Image.open(r"images jeu\Metallica.png")),
        'C-Moon' : ImageTk.PhotoImage(Image.open(r"images jeu\Cmoon.png")),
        'Enigma' : ImageTk.PhotoImage(Image.open(r"images jeu\Enigma.png")),
        'Akaza' : ImageTk.PhotoImage(Image.open(r"images jeu\akaza.png")),
        'Spider' : ImageTk.PhotoImage(Image.open(r"images jeu\spider.png").resize((50,50))),
        'Slender' : ImageTk.PhotoImage(Image.open(r"images jeu\slender.png").resize((55,55))),
        'Hoopa' : ImageTk.PhotoImage(Image.open(r"images jeu\hoopa.png")),
        'Merchant' : ImageTk.PhotoImage(Image.open(r"images jeu\Merchant.jpg")),
        'Mimic' : ImageTk.PhotoImage(Image.open(r"images jeu\Mimic.png")),
        'Kecleon' : ImageTk.PhotoImage(Image.open(r"images jeu\kecleon.png")),
        'MerchantIt' : ImageTk.PhotoImage(Image.open(r"images jeu\Merchant_pascontent.png")),
        'Regimelt' : ImageTk.PhotoImage(Image.open(r"images jeu\Regimelt.png")),
        'Mettaton' : ImageTk.PhotoImage(Image.open(r"images jeu\Mettaton.png")),



        
    },
    'items': {
        'TNT': ImageTk.PhotoImage(Image.open(r"images jeu\TNT.png")),
        'Health Pot': ImageTk.PhotoImage(Image.open(r"images jeu\healthpot.png")),
        'Invisible pot' : ImageTk.PhotoImage(Image.open(r"images jeu\invisiblePotion.png").resize((40,40))),
        'Rainbow Sword': ImageTk.PhotoImage(Image.open(r"images jeu\sword.png")),  ### à redim
        'Moonstaff': ImageTk.PhotoImage(Image.open(r"images jeu\moonstaff.png")),
        'Dogecoin' : ImageTk.PhotoImage(Image.open(r"images jeu\Dogecoin.png")),
        'Gun' : ImageTk.PhotoImage(Image.open(r"images jeu\coltPython.png")),
        'Bee' :  ImageTk.PhotoImage(Image.open(r"images jeu\Bee.png")),
        'Apple' : ImageTk.PhotoImage(Image.open(r"images jeu\apple_map.png").resize((40,40))),
        'Pizza' : ImageTk.PhotoImage(Image.open(r"images jeu\pizza.png").resize((40,40))),
        'Katana' : ImageTk.PhotoImage(Image.open(r"images jeu\katana.png")),
        'Blue Armor' : ImageTk.PhotoImage(Image.open(r"images jeu\blueArmor.png")),
        'Iron Armor' : ImageTk.PhotoImage(Image.open(r"images jeu\ironArmor.png")),
        'Chicken' : ImageTk.PhotoImage(Image.open(r"images jeu\chicken.png")),
        'Smith&Wesson' : ImageTk.PhotoImage(Image.open(r"images jeu\SmithAndWessonBodyguard638.png")),
        'MimicIt' : ImageTk.PhotoImage(Image.open(r"images jeu\MimicIt.png"))

    
    },    
    'hero': {
        "Hero" : ImageTk.PhotoImage(Image.open(r'images jeu\monokuma.png')),
        "HeroInv" : ImageTk.PhotoImage(Image.open(r"images jeu\monokuma_invisible.png")),

        
        "HeroCB": ImageTk.PhotoImage(Image.open(r"images jeu\monokumaCowBoy.png")),
        "HeroCBInvisible": ImageTk.PhotoImage(Image.open(r"images jeu\monokumaCowBoyInvisible.png")),
        
        
        'HeroSword' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaSword.png")),
        'HeroSwordInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaSwordInvisible.png")),
        
        'HeroKatana' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaKatana.png")),
        'HeroKatanaInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaKatanaInvisible.png")),
        'HeroBlueArmorKatana' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorKatana.png")),
        'HeroBlueArmorKatanaInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorKatanaInvisible.png")),

        'HeroIronArmor' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmor.png")),
        'HeroIronArmorInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorInvisible.png")),

        'HeroIronArmorKatana' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorKatana.png")),
        'HeroIronArmorKatanaInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorKatanaInvisible.png")),

        
        'HeroIronArmorRainbowSword' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorRainbowSword.png")),
        'HeroIronArmorRainbowSwordInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorRainbowSwordInvisible.png")),
        'HeroBlueArmorRainbowSword' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorRainbowSword.png")),
        'HeroBlueArmorRainbowSwordInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorRainbowSwordInvisible.png")),

        'HeroIronArmorCowBoy' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorCowBoy.png")),
        'HeroIronArmorCowBoyInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorCowBoyInvisible.png")),

        'HeroBlueArmor' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmor.png")),
        'HeroBlueArmorInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorInvisible.png")),
        'HeroBlueArmorCowBoy' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorCowBoy.png")),
        'HeroBlueArmorCowBoyInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorCowBoyInvisible.png")),

        'HeroMista' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaMista.png")),
        'HeroMistaInvisible' :ImageTk.PhotoImage(Image.open(r"images jeu\monokumaMistaInvisible.png")),
        'HeroBlueArmorMista' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorMista.png")),
        'HeroBlueArmorMistaInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorMistaInvisible.png")),
        'HeroIronArmorMista' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorMista.png")),
        'HeroIronArmorMistaInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorMistaInvisible.png")),

    },
    'interface' : 
        {'money' : ImageTk.PhotoImage(Image.open(r"images jeu\dogecoinCanvas.png")),
        'vie' : ImageTk.PhotoImage(Image.open(r"images jeu\heart.png")),
        'viePSN' : ImageTk.PhotoImage(Image.open(r"images jeu\heartpoison.png")),
        'select' : ImageTk.PhotoImage(Image.open(r"images jeu\selectArrow.png")),
        'circle' : ImageTk.PhotoImage(Image.open(r"images jeu\circle.png")),
        'Monosuke':ImageTk.PhotoImage(Image.open(r"images jeu\Monosuke test.png")),
        'Monotaro' : ImageTk.PhotoImage(Image.open(r"images jeu\Monotaro opacité.png")),
        'Monophanie' :ImageTk.PhotoImage(Image.open(r"images jeu\Monophanie opacité.png")),
        'Monokid' : ImageTk.PhotoImage(Image.open(r"images jeu\Monokid opacité.png")),
        'Monodam' : ImageTk.PhotoImage(Image.open(r"images jeu\Monodam opacité.png")),
        'Apple' : ImageTk.PhotoImage(Image.open(r'images jeu\apple.png')),
        'WoU' : ImageTk.PhotoImage(Image.open(r'images jeu\wonderOfU head.png')),
        'WoU opacité' : ImageTk.PhotoImage(Image.open(r'images jeu\wonderOfU head opacité.png')),
        'Strength' : ImageTk.PhotoImage(Image.open(r'images jeu\swordInterface.png')),
        'Shield' : ImageTk.PhotoImage(Image.open(r'images jeu\shield.png')),
        'Kills' : ImageTk.PhotoImage(Image.open(r'images jeu\kills.png'))


        },
    'inventaire' : {
        'Health Pot': ImageTk.PhotoImage(Image.open(r"images jeu\healthpot.png").resize((50,50))),
        'TNT' : ImageTk.PhotoImage(Image.open(r"images jeu\TNT.png").resize((50,75))),
        'Moonstaff' : ImageTk.PhotoImage(Image.open(r"images jeu\moonstaff.png").resize((50,75))),
        'Gun' : ImageTk.PhotoImage(Image.open(r"images jeu\coltPython.png").resize((72,72))),
        'Rainbow Sword': ImageTk.PhotoImage(Image.open(r"images jeu\sword.png")),  

    },
    'kids' :{
        'Monophanie' : ImageTk.PhotoImage(Image.open(r"images jeu\Monophanie.png")),
        'Monosuke' : ImageTk.PhotoImage(Image.open(r"images jeu\Monosuke.png")),
        'Monodam' : ImageTk.PhotoImage(Image.open(r"images jeu\Monodam.png")),
        'Monotaro' : ImageTk.PhotoImage(Image.open(r"images jeu\Monotaro.png")),
        'Monokid' : ImageTk.PhotoImage(Image.open(r"images jeu\Monokid.png"))
    },
    'season' :{
        'spring' : ImageTk.PhotoImage(Image.open(r"images jeu\spring.png")),
        'summer' : ImageTk.PhotoImage(Image.open(r"images jeu\summer.png")),
        'fall' : ImageTk.PhotoImage(Image.open(r"images jeu\fall.png")),
        'winter' : ImageTk.PhotoImage(Image.open(r"images jeu\winter.png")),
        'winter2' : ImageTk.PhotoImage(Image.open(r"images jeu\winter2.png")),

    }
}

window.bind('<KeyPress>',theGame().mainGame)
theGame().play()
window.mainloop()
