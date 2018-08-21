from copy import deepcopy

from framework.generic_samplers import *


class TestGenericClasses(object):
    def setUp(self):
        """Setup various shared variables and functionality"""
        # Set a seed to get reproducible test runs.
        random.seed(12345)

        Prod = ProdClass
        L = LAtomClass
        U = UAtomClass
        Z = ZeroAtomClass
        Set = SetClass

        self.obj1 = Prod(L(), Prod(U(), L()))  # l:2, u:1
        self.obj2 = Prod(Set([L(), U(), L()]), Prod(U(), U()))  # l:2, u:3
        self.obj3 = Prod(Z(), Z())  # l:0, u:0
        self.obj4 = Prod(L(), L())  # l:2, l:0
        self.obj5 = Prod(U(), U())  # l:0, u:2
        self.prod_objs = [self.obj1, self.obj2, self.obj3, self.obj4, self.obj5]
        self.prod_objs_sizes = [(2, 1), (2, 3), (0, 0), (2, 0), (0, 2)]

        self.set_objs = []
        self.set_objs_sizes = []

        class FakeSampler(object):
            def __init__(self, obj):
                self.obj = obj

            def sample(self, x, y):
                return deepcopy(self.obj)

            def l_size_sampled_object(self):
                return self.obj.l_size

            def u_size_sampled_object(self):
                return self.obj.u_size

        self.fake_sampler = FakeSampler(self.obj1)

        Settings.debug_mode = True

    def test_dummy_class(self):
        l_sizes = [0, 1, 2, 5, 42]
        u_sizes = [0, 1, 4, 5, 42]
        # Arbitrary numbers here as the atoms of dummy classes do not explicitly exist.
        exceptions = [[], [1], [1, 2], [1, 2, 3, 4, 5]]
        for l_size in l_sizes:
            for u_size in u_sizes:
                dummy = DummyClass(l_size, u_size)
                assert dummy.l_size == l_size
                assert dummy.u_size == u_size
                for excp in exceptions:
                    dummy = DummyClass(l_size, u_size)
                    try:
                        dummy = dummy.replace_l_atoms(self.fake_sampler, 'x', 'y', excp)
                        assert dummy.l_size == (l_size - len(excp)) * self.fake_sampler.l_size_sampled_object() + len(excp)
                        assert dummy.u_size == u_size + (l_size - len(excp)) * self.fake_sampler.u_size_sampled_object()
                    except BoltzmannFrameworkError:
                        pass
                for excp in exceptions:
                    dummy = DummyClass(l_size, u_size)
                    try:
                        dummy = dummy.replace_u_atoms(self.fake_sampler, 'x', 'y', excp)
                        assert dummy.l_size == l_size + (u_size - len(excp)) * self.fake_sampler.l_size_sampled_object()
                        assert dummy.u_size == (u_size - len(excp)) * self.fake_sampler.u_size_sampled_object() + len(excp)
                    except BoltzmannFrameworkError:
                        pass

    def test_prod_class(self):
        for index, obj in enumerate(self.prod_objs):
            assert obj.l_size == self.prod_objs_sizes[index][0]
            assert obj.u_size == self.prod_objs_sizes[index][1]
        for obj in self.prod_objs:
            gamma = deepcopy(obj)
            gamma = gamma.replace_l_atoms(self.fake_sampler, 'x', 'y')
            assert gamma.l_size == obj.l_size * self.fake_sampler.l_size_sampled_object()
            assert gamma.u_size == obj.u_size + obj.l_size * self.fake_sampler.u_size_sampled_object()
            gamma = deepcopy(obj)
            gamma = gamma.replace_u_atoms(self.fake_sampler, 'x', 'y')
            assert gamma.l_size == obj.l_size + obj.u_size * self.fake_sampler.l_size_sampled_object()
            assert gamma.u_size == obj.u_size * self.fake_sampler.u_size_sampled_object()

    def test_set_class(self):
        pass

    def test_assign_random_labels(self):
        for obj in self.prod_objs:
            gamma = deepcopy(obj)
            gamma.assign_random_labels()

    def test_derived_class(self):
        obj1_dx = LDerivedClass(self.obj1)
        assert str(obj1_dx) == str(self.obj1) + '_dx'
        assert obj1_dx.l_size == self.obj1.l_size - 1
        obj1_dx_dy = UDerivedClass(obj1_dx)
        assert obj1_dx_dy.l_size == self.obj1.l_size - 1
        assert obj1_dx_dy.u_size == self.obj1.u_size - 1
        assert str(obj1_dx_dy) == str(self.obj1) + '_dx_dy'
        print(obj1_dx_dy)
        obj1_dy_dx = obj1_dx_dy.invert_derivation_order()
        assert str(obj1_dy_dx) == str(self.obj1) + '_dy_dx'
        print(obj1_dy_dx)


if __name__ == "__main__":
    test = TestGenericClasses()
    test.setUp()
    test.test_dummy_class()
    test.test_prod_class()
    test.test_set_class()
    test.test_assign_random_labels()
    test.test_derived_class()
