class Boundary:
    def title(self): return self.__class__.__name__
class LoginBoundary(Boundary): pass
class AdminBoundary(Boundary): pass
class CompanyBoundary(Boundary): pass
class DesignerPortfolioBoundary(Boundary): pass
class CustomerExploreBoundary(Boundary): pass
class FavouriteBoundary(Boundary): pass
class PlatformBoundary(Boundary): pass
