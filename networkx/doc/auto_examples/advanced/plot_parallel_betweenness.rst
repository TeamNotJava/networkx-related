

.. _sphx_glr_auto_examples_advanced_plot_parallel_betweenness.py:


====================
Parallel Betweenness
====================

Example of parallel implementation of betweenness centrality using the
multiprocessing module from Python Standard Library.

The function betweenness centrality accepts a bunch of nodes and computes
the contribution of those nodes to the betweenness centrality of the whole
network. Here we divide the network in chunks of nodes and we compute their
contribution to the betweenness centrality of the whole network.

This doesn't work in python2.7.13. It does work in 3.6, 3.5, 3.4, and 3.3.

It may be related to this:
https://stackoverflow.com/questions/1816958/cant-pickle-type-instancemethod-when-using-multiprocessing-pool-map




.. code-block:: pytb

    Traceback (most recent call last):
      File "/Users/valkum/git/networkx/examples/advanced/plot_parallel_betweenness.py", line 77, in <module>
        bt = betweenness_centrality_parallel(G)
      File "/Users/valkum/git/networkx/examples/advanced/plot_parallel_betweenness.py", line 57, in betweenness_centrality_parallel
        node_chunks))
      File "/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/lib/python3.6/multiprocessing/pool.py", line 266, in map
        return self._map_async(func, iterable, mapstar, chunksize).get()
      File "/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/lib/python3.6/multiprocessing/pool.py", line 644, in get
        raise self._value
      File "/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/lib/python3.6/multiprocessing/pool.py", line 424, in _handle_tasks
        put(task)
      File "/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/lib/python3.6/multiprocessing/connection.py", line 206, in send
        self._send_bytes(_ForkingPickler.dumps(obj))
      File "/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/lib/python3.6/multiprocessing/reduction.py", line 51, in dumps
        cls(buf, protocol).dump(obj)
    _pickle.PicklingError: Can't pickle <function _betmap at 0x10e540bf8>: attribute lookup _betmap on __main__ failed





.. code-block:: python


    from multiprocessing import Pool
    import time
    import itertools

    import matplotlib.pyplot as plt
    import networkx as nx


    def chunks(l, n):
        """Divide a list of nodes `l` in `n` chunks"""
        l_c = iter(l)
        while 1:
            x = tuple(itertools.islice(l_c, n))
            if not x:
                return
            yield x


    def _betmap(G_normalized_weight_sources_tuple):
        """Pool for multiprocess only accepts functions with one argument.
        This function uses a tuple as its only argument. We use a named tuple for
        python 3 compatibility, and then unpack it when we send it to
        `betweenness_centrality_source`
        """
        return nx.betweenness_centrality_source(*G_normalized_weight_sources_tuple)


    def betweenness_centrality_parallel(G, processes=None):
        """Parallel betweenness centrality  function"""
        p = Pool(processes=processes)
        node_divisor = len(p._pool) * 4
        node_chunks = list(chunks(G.nodes(), int(G.order() / node_divisor)))
        num_chunks = len(node_chunks)
        bt_sc = p.map(_betmap,
                      zip([G] * num_chunks,
                          [True] * num_chunks,
                          [None] * num_chunks,
                          node_chunks))

        # Reduce the partial solutions
        bt_c = bt_sc[0]
        for bt in bt_sc[1:]:
            for n in bt:
                bt_c[n] += bt[n]
        return bt_c


    if __name__ == "__main__":
        G_ba = nx.barabasi_albert_graph(1000, 3)
        G_er = nx.gnp_random_graph(1000, 0.01)
        G_ws = nx.connected_watts_strogatz_graph(1000, 4, 0.1)
        for G in [G_ba, G_er, G_ws]:
            print("")
            print("Computing betweenness centrality for:")
            print(nx.info(G))
            print("\tParallel version")
            start = time.time()
            bt = betweenness_centrality_parallel(G)
            print("\t\tTime: %.4F" % (time.time() - start))
            print("\t\tBetweenness centrality for node 0: %.5f" % (bt[0]))
            print("\tNon-Parallel version")
            start = time.time()
            bt = nx.betweenness_centrality(G)
            print("\t\tTime: %.4F seconds" % (time.time() - start))
            print("\t\tBetweenness centrality for node 0: %.5f" % (bt[0]))
        print("")

        nx.draw(G_ba)
        plt.show()

**Total running time of the script:** ( 0 minutes  0.000 seconds)



.. only :: html

 .. container:: sphx-glr-footer


  .. container:: sphx-glr-download

     :download:`Download Python source code: plot_parallel_betweenness.py <plot_parallel_betweenness.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: plot_parallel_betweenness.ipynb <plot_parallel_betweenness.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
