# -*- coding: utf-8 -*-
#    Copyright (C) 2018 by
#    Marta Grobelna <marta.grobelna@rwth-aachen.de>
#    Petre Petrov <petrepp4@gmail.com>
#    Rudi Floren <rudi.floren@gmail.com>
#    Tobias Winkler <tobias.winkler1@rwth-aachen.de>
#    All rights reserved.
#    BSD license.
#
# Authors:  Marta Grobelna <marta.grobelna@rwth-aachen.de>
#           Petre Petrov <petrepp4@gmail.com>
#           Rudi Floren <rudi.floren@gmail.com>
#           Tobias Winkler <tobias.winkler1@rwth-aachen.de>

from planar_graph_sampler.combinatorial_classes.network import Network


def merge_networks_in_series(n1, n2):
    """Merges the `n2` into `n1` in a serial manner
    which means that the infinite pole from `n1` is identified with the
    0-pole from `n2`.

    Parameters
    ----------
    n1: Network
        First network which will result in merged networks.
    n2: Network
        Second network which will be plugged into the first one.

    Returns
    -------
    Network
        The network resulting from the serial merge operation.
    """
    new_l_size = n1.l_size + n2.l_size + 1  # One additional vertex in between.
    new_u_size = n1.u_size + n2.u_size

    # Connect the 0-pole and the inf-pole in the result network.
    new_link_edge = n1.zero_pole.insert_before()
    new_link_edge_opp = n2.inf_pole.insert_after()
    new_link_edge.opposite = new_link_edge_opp
    new_link_edge_opp.opposite = new_link_edge

    # Merge the 0-pole of n1 with the inf-pole of n2.
    n1.inf_pole.insert_all_after(n2.zero_pole)

    # Remove the link edges in n1 and n2 if they are not real.
    if not n1.is_linked:
        n1.zero_pole.remove()
        n1.inf_pole.remove()
    if not n2.is_linked:
        n2.zero_pole.remove()
        n2.inf_pole.remove()

    # After a serial merge the poles are never linked.
    res = Network(new_link_edge, is_linked=False, l_size=new_l_size, u_size=new_u_size)
    res.type = 'S'
    return res

    # # Extract the poles from both networks.
    # first_net_zero_pole_edge = n1.zero_pole
    # first_net_inf_pole_edge = n1.inf_pole
    #
    # second_net_zero_pole_edge = n2.zero_pole
    # second_net_inf_pole_edge = n2.inf_pole
    #
    # # Create a new half edges for connecting the poles of the network. The
    # # edge will not be part from the edges list.
    # new_root_half_edge = first_net_zero_pole_edge.insert_after()
    # new_root_opposite = second_net_inf_pole_edge.insert_after()
    #
    # new_root_half_edge.opposite = new_root_opposite
    # new_root_opposite.opposite = new_root_half_edge
    #
    # # Get the half edges from both networks for merging
    # first_net_inf_pole_prior = first_net_inf_pole_edge.prior
    # second_net_zero_pole_edge_prior = second_net_zero_pole_edge.prior
    #
    # # Merge the both networks so that the inf-pole from the first network is
    # #  identified with the zero-pole from the second one. Handling different
    # #  while merging the two networks.
    # first_net_inf_pole_edge.prior = second_net_zero_pole_edge_prior
    # second_net_zero_pole_edge_prior.next = first_net_inf_pole_edge
    #
    # first_net_inf_pole_prior.next = second_net_zero_pole_edge
    # second_net_zero_pole_edge.prior = first_net_inf_pole_prior
    #
    # # Update the node numbers in the second network zero-pole edges
    # half_edge_walker = first_net_inf_pole_prior.next
    # while half_edge_walker != first_net_inf_pole_prior:
    #     half_edge_walker.node_nr = first_net_inf_pole_edge.node_nr
    #     half_edge_walker = half_edge_walker.next
    #
    # # Check whether the original poles of the network that are merged are
    # # linked or not. If they are not linked then the corresponding half
    # # edges between them have to be removed.
    # if not n1.is_linked:
    #     # Remove the half edges between the zero and inf pole from the first
    #     #  network.
    #     first_net_zero_pole_edge.remove()
    #     first_net_inf_pole_edge.remove()
    #
    # if not n2.is_linked:
    #     # Remove the half edges between the zero and inf pole from the first
    #     #  network.
    #     second_net_zero_pole_edge.remove()
    #     second_net_inf_pole_edge.remove()
    #
    # # After a serial merge the poles are never linked.
    # res = Network(new_root_half_edge, is_linked=False,
    #                l_size=new_l_size, u_size=new_u_size)
    # res.type = 'S'
    # return res


def merge_networks_in_parallel(n1, n2):
    """Merges network `n1` and network `n2` in parallel which
    means their respective inf-poles and 0-poles coincide.

    Parameters
    ----------
    n1: Network
        First network which will result in merged networks.
    n2: Network
        Second network which will be plugged into the first one.

    Returns
    -------
    Network
        The network resulting from the parallel merge operation.
    """
    # This operation is not defined if both networks are linked.
    assert not (n1.is_linked and n2.is_linked), (n1, n2)

    if n1.is_linked:
        return merge_networks_in_parallel(n2, n1)

    # Either n2 is linked and n1 not or both are not linked.
    assert not n1.is_linked

    new_l_size = n1.l_size + n2.l_size
    new_u_size = n1.u_size + n2.u_size
    res_is_linked = n1.is_linked or n2.is_linked

    # Merge 0-poles.
    n1.zero_pole.insert_all_before(n2.zero_pole.prior)

    # Merge inf-poles.
    n1.inf_pole.insert_all_after(n2.inf_pole.next)

    # Remove the link edge in n1
    n1.zero_pole.remove()
    n1.inf_pole.remove()

    res = Network(n2.zero_pole, res_is_linked, new_l_size, new_u_size)
    res.type = 'P'
    return res

    # # Merge their 0-poles.
    # first_net_zero_pole_prior = first_net_zero_pole_edge.prior
    # second_net_zero_pole_next = second_net_zero_pole_edge.next
    # second_net_zero_pole_prior = second_net_zero_pole_edge.prior
    # first_net_zero_pole_edge.prior = second_net_zero_pole_prior
    # second_net_zero_pole_prior.next = first_net_zero_pole_edge
    # first_net_zero_pole_prior.next = second_net_zero_pole_next
    # second_net_zero_pole_next.prior = first_net_zero_pole_prior
    #
    # # Update the node numbers in the zero pole.
    # half_edge_walker = first_net_zero_pole_edge.next
    # while half_edge_walker != first_net_zero_pole_edge:
    #     half_edge_walker.node_nr = first_net_zero_pole_edge.node_nr
    #     half_edge_walker = half_edge_walker.next

    # # Merge their inf-poles
    # first_net_inf_pole_next = first_net_inf_pole_edge.next
    # second_net_inf_pole_prior = second_net_inf_pole_edge.prior
    # second_net_inf_pole_next = second_net_inf_pole_edge.next
    # first_net_inf_pole_edge.next = second_net_inf_pole_next
    # second_net_inf_pole_next.prior = first_net_inf_pole_edge
    # first_net_inf_pole_next.prior = second_net_inf_pole_prior
    # second_net_inf_pole_prior.next = first_net_inf_pole_next
    #
    # # Update the node numbers in the inf pole
    # half_edge_walker = first_net_inf_pole_edge.next
    # while half_edge_walker != first_net_inf_pole_edge:
    #     half_edge_walker.node_nr = first_net_inf_pole_edge.node_nr
    #     half_edge_walker = half_edge_walker.next


def substitute_edge_by_network(half_edge_for_sub, network):
    """Substitute the edge from the three connected graph with the whole
    network given as an argument.

    Parameters
    ----------
    half_edge_for_sub: HalfEdge
        The half edge in a three connected graph whose corresponding full edge
        is substituted.
    network: Network
        The network to plug in.
    """

    assert half_edge_for_sub.opposite is not None
    assert half_edge_for_sub.next is not None
    assert half_edge_for_sub.opposite.next is not None

    # Plug it in.
    half_edge_for_sub.insert_all_before(network.zero_pole.prior)
    half_edge_for_sub.opposite.insert_all_after(network.inf_pole.next)

    # Remove the link edge of the network if it is not real.
    if not network.is_linked:
        network.zero_pole.remove()
        network.inf_pole.remove()

    # Remove the substituted half-edge.
    half_edge_for_sub.remove()
    half_edge_for_sub.opposite.remove()


    # # Extract the opposite half edge from the tree connected graph.
    # half_edge_for_sub_opp = half_edge_for_sub.opposite
    #
    # # Get the needed edges for manipulation from the network.
    # net_root_half_edge = network.zero_pole
    # net_root_half_edge_next = net_root_half_edge.next
    # net_root_half_edge_prior = net_root_half_edge.prior
    # net_root_half_edge_opp_next = net_root_half_edge.opposite.next
    # net_root_half_edge_opp_prior = net_root_half_edge.opposite.prior
    #
    # # Identify the zero pole with the the half_edge_for_sub vertex.
    # half_edge_for_sub.opposite = net_root_half_edge_next.opposite
    # net_root_half_edge_next.opposite.opposite = half_edge_for_sub
    # if net_root_half_edge_next is not net_root_half_edge_prior:
    #     # Switch the pointers so that the network_root_edge and its next are
    #     #  not included
    #     half_edge_for_sub_next = half_edge_for_sub.next
    #
    #     half_edge_for_sub.next = net_root_half_edge_next.next
    #     net_root_half_edge_next.next.prior = half_edge_for_sub
    #
    #     half_edge_for_sub_next.prior = net_root_half_edge_prior
    #     net_root_half_edge_prior.next = half_edge_for_sub_next
    #
    #     # Update the node numbers in the _second network zero-pole half edges
    #     half_edge_walker = half_edge_for_sub.next
    #     while half_edge_walker != half_edge_for_sub:
    #         half_edge_walker.node_nr = half_edge_for_sub.node_nr
    #         half_edge_walker = half_edge_walker.next
    #
    # # Identify the inf pole with the the half_edge_for_sub_opp vertex.
    # half_edge_for_sub_opp.opposite = net_root_half_edge_opp_next.opposite
    # net_root_half_edge_opp_next.opposite.opposite = half_edge_for_sub_opp
    # if net_root_half_edge_opp_next is not net_root_half_edge_opp_prior:
    #     # Switch the pointers so that the network_root_edge_opp and its next
    #     #  are not included
    #     half_edge_for_sub_opp_next = half_edge_for_sub_opp.next
    #
    #     half_edge_for_sub_opp.next = net_root_half_edge_opp_next.next
    #     net_root_half_edge_opp_next.next.prior = half_edge_for_sub_opp
    #
    #     half_edge_for_sub_opp_next.prior = net_root_half_edge_opp_prior
    #     net_root_half_edge_opp_prior.next = half_edge_for_sub_opp_next
    #
    #     half_edge_walker = half_edge_for_sub_opp.next
    #     while half_edge_walker != half_edge_for_sub_opp:
    #         half_edge_walker.node_nr = half_edge_for_sub_opp.node_nr
    #         half_edge_walker = half_edge_walker.next
