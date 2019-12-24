import pygame as py
import time
import math
import random
from threading import Event
vec = py.math.Vector2

def collideHitRect(sprite1, sprite2):
    return sprite1.hit_rect.colliderect(sprite2)

def wallDetection(dir, sprite, group):  #sets cannon's x velocity to zero if it hits the left or right side of a wall, same idea for y velocity
    if dir == 'x':
        hits = py.sprite.spritecollide(sprite, group, False, collideHitRect)
        if hits:
            if sprite.vel.x > 0:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width/2
            if sprite.vel.x < 0:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width/2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = py.sprite.spritecollide(sprite, group, False, collideHitRect)
        if hits:
            if sprite.vel.y > 0:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height/2
            if sprite.vel.y < 0:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height/2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Cannon(py.sprite.Sprite):

    def __init__(self, x_cor, y_cor, dt, img, walls, trenches):
        py.sprite.Sprite.__init__(self)
        self.img = img
        self.dt = dt
        self.walls = walls
        self.trenches = trenches
        self.width, self.height = 96,96
        self.image =  py.transform.scale(py.image.load(self.img).convert_alpha(), (self.width, self.height))
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.hit_rect = py.Rect(0,0,64,64)
        self.hit_rect.center = self.rect.center
        self.pos = vec(x_cor , y_cor)
        self.rot_vel = 0
        self.rot = 0

    def update(self):

        cursor = py.mouse.set_cursor(*py.cursors.broken_x)
        self.getKeys()
        degrees = self.getMouseAngle()

        self.pos += self.vel * self.dt
        self.rot = (self.rot + self.rot_vel * self.dt) % 360
        self.image = py.transform.rotate(self.orig_image, degrees)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        wallDetection('x', self, self.walls)
        wallDetection('x', self, self.trenches)
        self.hit_rect.centery = self.pos.y
        wallDetection('y', self, self.walls)
        wallDetection('y', self, self.trenches)

    def getKeys(self):

        keys = py.key.get_pressed()
        self.vel = vec(0,0)
        self.rot_vel = 0

        if keys[py.K_w] : #forwards
            self.vel = vec(150, 0).rotate(-self.rot)

        if keys[py.K_a]:   #rotate left
            self.rot_vel = 100

        if keys[py.K_s]:  #reverse
            self.vel = vec(-50, 0).rotate(-self.rot)

        if keys[py.K_d]:  #rotate right
            self.rot_vel = -100



    def getMouseAngle(self):

        self.mouse_pos = py.mouse.get_pos()
        dy = self.mouse_pos[1] - self.pos.y
        dx = self.mouse_pos[0] - self.pos.x
        radians = math.atan2(-dy,dx)
        degrees = math.degrees(radians)
        return degrees

    def getMouseAngleRad(self):
        return math.radians(self.getMouseAngle())

class Player(py.sprite.Sprite):

    def __init__(self, x_cor, y_cor, dt, img, walls, trenches):

        py.sprite.Sprite.__init__(self)
        self.width,self.height = 64,64
        self.img = img
        self.dt = dt
        self.image = py.transform.scale(py.image.load(self.img).convert_alpha(), (self.width, self.height))
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.hit_rect = py.Rect(0, 0, self.width, self.height)  #used for wall collision
        self.hit_rect.center = self.rect.center
        self.walls = walls
        self.trenches = trenches
        self.pos = vec(x_cor, y_cor)
        self.rot = 0

    def update(self):

        self.getKeys()
        self.pos += self.vel * self.dt
        self.rot = (self.rot + self.rot_vel * self.dt) % 360
        self.image = py.transform.rotate(self.orig_image, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        wallDetection('x', self, self.walls)
        wallDetection('x', self, self.trenches)
        self.hit_rect.centery = self.pos.y
        wallDetection('y', self, self.walls)
        wallDetection('y', self, self.trenches)

    def getKeys(self):

        self.keys = py.key.get_pressed()
        self.vel = vec(0, 0)
        self.rot_vel = 0

        if self.keys[py.K_w] : #forwards
            self.vel = vec(150, 0).rotate(-self.rot)

        if self.keys[py.K_a]:   #rotate left
            self.rot_vel = 100

        if self.keys[py.K_s]:  #reverse
            self.vel = vec(-50, 0).rotate(-self.rot)

        if self.keys[py.K_d]:  #rotate right
            self.rot_vel = -100

class Enemy(py.sprite.Sprite):

    def __init__(self, x_cor, y_cor, img, dt, player_pos, walls, trenches, type):
        py.sprite.Sprite.__init__(self)
        self.width, self.height = 64,64
        self.img = img
        self.type = type
        self.walls = walls
        self.trenches = trenches
        self.dt = dt
        self.player_pos = player_pos
        self.image = py.transform.scale(py.image.load(self.img).convert_alpha(), (self.width, self.height))
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.hit_rect = py.Rect(0, 0, self.width, self.height)
        self.hit_rect.center = self.rect.center
        self.pos = vec(x_cor, y_cor)
        self.vel = vec(0,0)
        self.acc = vec(0,0)

    def update(self):

        self.rect.center = self.pos
        if self.type == 'G':
            #angular
            self.rot = (self.player_pos - self.pos).angle_to(vec(1,1))
            #linear
            self.acc = vec(100, 0).rotate(-self.rot)
            self.acc += self.vel * -1
            self.vel += self.acc * self.dt
            self.pos += self.vel * self.dt + 0.5 * self.acc * self.dt**2
            self.image = py.transform.rotate(self.orig_image, self.rot + 90)
            self.rect = self.image.get_rect()
            self.hit_rect.centerx = self.pos.x
            wallDetection('x', self, self.walls)
            wallDetection('x', self, self.trenches)
            self.hit_rect.centery = self.pos.y
            wallDetection('y', self, self.walls)
            wallDetection('y', self, self.trenches)
            self.rect.center = self.pos

class Turret(py.sprite.Sprite):

    def __init__(self, x_cor, y_cor, img, dt, player_pos, walls, trenches, type):
        py.sprite.Sprite.__init__(self)
        self.img = img
        self.type = type
        self.walls = walls
        self.trenches = trenches
        self.dt = dt
        self.width, self.height = 96,96
        self.player_pos = player_pos
        self.image = py.transform.scale(py.image.load(self.img).convert_alpha(), (self.width,self.height))
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.hit_rect = py.Rect(0, 0, 64, 64)
        self.hit_rect.center = self.rect.center
        self.pos = vec(x_cor, y_cor)
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.rot = 0
        self.bullet_image =  'assets/bulletSilver_outline.png'

    def update(self):


        #angular movement
        self.point_deg = (self.player_pos - self.pos).angle_to(vec(1,0))  # Subtracting both postion vectors creates a new vector directly from enemy to the player, then finds the angle between the x axis and this new vec.
        self.point_rad = math.radians(self.point_deg)
        self.image = py.transform.rotate(self.orig_image, self.point_deg)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        if self.type == 'G':

            #linear movement
            self.rot = (self.player_pos - self.pos).angle_to(vec(1,1))
            self.acc = vec(100, 0).rotate(-self.rot)
            self.acc += self.vel * -1
            self.vel += self.acc * self.dt
            self.pos += self.vel * self.dt + 0.5 * self.acc * self.dt**2
            self.hit_rect.centerx = self.pos.x
            wallDetection('x', self, self.walls)
            wallDetection('x', self, self.trenches)
            self.hit_rect.centery = self.pos.y
            wallDetection('y', self, self.walls)
            wallDetection('y', self, self.trenches)
            self.rect.center = self.pos

    def shoot(self):

        self.bullet = Projectile(self.pos.x + self.width*math.cos(self.point_rad), self.pos.y - self.height*math.sin(self.point_rad), self.point_deg, self.dt, self.bullet_image, self.walls)

class Projectile(py.sprite.Sprite):
    def __init__(self, x_pos, y_pos, angle, dt, img, walls):

        py.sprite.Sprite.__init__(self)
        self.img = img
        self.dt = dt
        self.walls = walls
        self.angle = angle
        self.image = py.transform.scale(py.image.load(self.img).convert_alpha(), (24,12))
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.hit_rect = py.Rect(0,0,1,1)
        self.hit_rect.center = self.rect.center
        self.wall_hit_flag = False
        self.pos = vec(x_pos, y_pos)
        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y
        self.image =  py.transform.rotate(self.orig_image, self.angle)
        self.ricochete = py.mixer.Sound('assets/ricochete.wav')

    def update(self):

        #if not Enemy.collideWithAnyWall(self):
        self.move()
        self.pos += self.vel * self.dt
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        self.hit_rect.centery = self.pos.y

    def move(self):           #ricochete logic

        if not self.collideWithWall('x') and not self.collideWithWall('y') and not self.wall_hit_flag:
            self.vel = vec(200, 0).rotate(-self.angle)

        else:

            if self.collideWithWall('x'):

                if not self.wall_hit_flag:
                    self.ricochete.play()
                    self.vel.x *= -1
                    self.wall_hit_flag = True
                    self.image = py.transform.rotate(self.orig_image, -self.angle)

                elif self.collideWithAnyWall():
                    self.kill()
                    self.wall_hit_flag = False

            if self.collideWithWall('y'):

                if not self.wall_hit_flag:
                    self.ricochete.play()
                    self.vel.y *= -1
                    self.wall_hit_flag = True
                    self.image = py.transform.rotate(self.orig_image, -self.angle)

                elif self.collideWithAnyWall():
                    self.kill()
                    self.wall_hit_flag = False

    def collideWithWall(self, dir):
        try:
            if dir == 'x':
                hits = py.sprite.spritecollide(self, self.walls, False)
                if hits:
                    if self.vel.x > 0:
                        if hits[0].rect.top < self.rect.centery and hits[0].rect.left > self.rect.centerx:
                            hits = hits.clear()
                            return True
                        else:
                            return False
                    elif self.vel.x < 0:
                        if hits[0].rect.top < self.rect.centery and hits[0].rect.right < self.rect.centerx:
                            hits = hits.clear()
                            return True
                        else:
                            return False
            if dir == 'y':
                hits = py.sprite.spritecollide(self, self.walls, False)
                if hits:
                    if self.vel.y > 0:
                        if hits[0].rect.right > self.rect.centerx and hits[0].rect.top > self.rect.centery:
                            hits = hits.clear()
                            return True
                        else:
                            return False

                    elif self.vel.y < 0:
                        if hits[0].rect.right > self.rect.centerx and hits[0].rect.bottom < self.rect.centery:
                            hits = hits.clear()
                            return True
                        else:
                            return False
        except:
            self.kill()

    def collideWithAnyWall(self):

        hits = py.sprite.spritecollideany(self, self.walls)

        if hits:
            return True
        else:
            return False

class Wall(py.sprite.Sprite):
    def __init__(self, x, y, walls, img):

        self.groups =  walls
        py.sprite.Sprite.__init__(self, self.groups)
        self.tile_size = 64
        self.img = img
        self.image = py.image.load(self.img)
        self.image = py.transform.scale(self.image, (self.tile_size, self.tile_size))
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.rect.x = x * self.tile_size    #spacing
        self.rect.y = y * self.tile_size
