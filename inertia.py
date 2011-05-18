#######################################################################
#
# Copyright (C) 2011 Steve Butler, Jason Grout.
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#######################################################################


class InertiaSet(object):

    def __init__(self, generators):
        self.generators=set(generators)
        self.generators.update([(y,x) for x,y in self.generators])
        self.reduce()

    def __add__(self, right):
        """
        Minkowski sum of self and right
        """
        from itertools import product
        return InertiaSet([(r1+r2, s1+s2) for ((r1,s1),(r2,s2)) in product(self.generators,
                                                                         right.generators)])

    def union(self, other):
        if isinstance(other, InertiaSet):
            return InertiaSet(self.generators.union(other.generators))
        else:
            return InertiaSet(self.generators.union(other))
    
    __or__=union

    def reduce(self):
        self.generators=set([x for x in self.generators 
                             if not any(x!=y and x[0]>=y[0] and x[1]>=y[1] 
                                        for y in self.generators)])

    def __repr__(self):
        return "Extended Inertia Set generated by %s"%self.generators

    def __eq__(self, other):
        # assume that both InertiaSets are reduced.
        return self.generators==other.generators
    
    def __contains__(self, p):
        return any(x[0]<=p[0] and x[1]<=p[1] for x in self.generators)

    def plot(self, *args, **kwargs):
        from sage.all import points
        max_tick=max(i[0] for i in self.generators)
        defaults=dict(pointsize=70,gridlines=True,
                ticks=[range(max_tick+1),range(max_tick+1)],
                aspect_ratio=1)
        defaults.update(kwargs)
        return points(self.generators, *args, **defaults)


import random
one_one=InertiaSet([(1,1)])
def inertia_set(g, f):
    global inertia_cache
    g6=g.canonical_label().graph6_string()
    if g6 in inertia_cache:
        return inertia_cache[g6]
    components=g.connected_components_subgraphs()
    I=InertiaSet([(0,0)])
    for c in components:
        try:
            #print I
            I+=f(c)
            #print I
        except ValueError:
            try:
                cut_vertex=random.choice(c.blocks_and_cut_vertices()[1])
            except IndexError:
                raise ValueError("Can not decompose unknown graph further", c)
            h=c.copy()
            h.delete_vertex(cut_vertex)
            component_inertia=inertia_set(h,f)+one_one
            component_inertia|=sum((inertia_set(c.subgraph(cc+[cut_vertex]),f) 
                                               for cc in h.connected_components()), 
                                   InertiaSet([(0,0)]))
            I+=component_inertia
    inertia_cache[g6]=I
    return I


inertia_cache = dict()
def f(g):
    global inertia_cache
    g6=g.canonical_label().graph6_string()
    if g6 in inertia_cache:
        return inertia_cache[g6]
    elif g.order()==1:
        return InertiaSet([(0,0)])
    elif g.order()==2 and g.size()==1:
        return InertiaSet([(0,1)])
    elif g.degree_sequence()[0]==g.order()-1 and g.degree_sequence()[1]==1:
        # g is a star
        return InertiaSet([(1,1), (g.order()-1,0)])
    
    raise ValueError("Do not know inertia set")

    

