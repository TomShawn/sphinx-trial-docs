
冬日，在暖暖的午后，泡上一杯茶，随便拿起一本书，凑到阳光跟前，是何等的惬意与享受……

风虽然不大，但走在路上，鼻子冷的刺骨的疼；而阳光却那么地温热，温热地忍不住想和她亲吻。

我泡上一杯碧螺春，从书架上随便拿起一本书，走向靠窗的位置，凑到阳光面前，任由她吻着我的脸，就像吻着自己的情人，这感觉美好的让你忘却了所有的烦恼。

.. .. sidebar:: 这是一个侧边栏

..     这是一个侧边栏, 可以放入代码, 也可以放入图像代码等等, 它下面可以是文字, 图像, 代码等等, 如本例中下面是一段文字.

.. 也许是身边暖气的缘故，空气的影子，映衬到桌子上、书纸上。影影绰绰如月下之花影，飘飘忽忽如山间之云气，生生腾腾如村落之炊烟，荡荡漾漾如湖面之微波，似乎在这图书馆的这一隅便可看尽天地间的朴素与祥和。

.. table:: Grid Table Demo
   :name: table-gridtable

   +------------------------+----------+----------+----------+
   | Header row, column 1   | Header 2 | Header 3 | Header 4 |
   | (header rows optional) |          |          |          |
   +========================+==========+==========+==========+
   | body row 1, column 1   | column 2 | column 3 | column 4 |
   +------------------------+----------+----------+----------+
   | body row 2             | ...      | ...      |          |
   +------------------------+----------+----------+----------+


.. csv-table:: Frozen Delights!
   :header: "Treat", "Quantity", "Description"
   :widths: 15, 10, 30

   "Albatross", 2.99, "On a stick!"
   "Crunchy Frog", 1.49, "If we took the bones out, it wouldn't be
   crunchy, now would it?"
   "Gannet Ripple", 1.99, "On a stick!"

.. 这是一个注释, 你只能在源码中看到我, 我不会被渲染出来.

..
   这整个缩进块都是
   一个注释.
   你只能在源码中看到我们, 我们不会被渲染出来

   仍是一个评论.

你可以看到我, 我不是注释.

.. caution::
    some notes
    sjdjdkk

      dddkdkk

      .. code-block:: sql

       CREATE TABLE


:guilabel:`Action`

:kbd:`Ctrl+Shift`

:menuselection:`A-->B-->C`

.. code-block:: python
   :caption: Code Blocks can have captions.
   :linenos:
   :emphasize-lines: 3,5

   def some_function():
       interesting = False
       print 'This line is highlighted.'
       print 'This one is not...'
       print '...but this one is.'


.. tip:: This is a tip

.. note:: This is a note

.. hint:: This is a hint

.. danger:: This is a danger

.. error:: This is an error

.. warning:: This is a warning

.. caution:: This is a caution

.. attention:: This is an attention

.. important:: This is an importsant

.. seealso:: This is seealso


.. topic:: Topic Title

    Subsequent indented lines comprise
    the body of the topic, and are
    interpreted as body elements.

撰写与发布
++++++++++++++

该手册采用reStructuredText标记语言撰写, 使用Sphinx进行发布.

.. table:: Grid Table Demo
   :name: table-gridtable
   :align: left

   +----------+--------------------------------------------------+
   | 属性     | 值                                               |
   +==========+==================================================+
   | 开发语言 | reStructuredText                                 |
   +----------+--------------------------------------------------+
   | 发布工具 | `Sphinx <http://www.sphinx-doc.org/en/stable/>`_ |
   +----------+--------------------------------------------------+