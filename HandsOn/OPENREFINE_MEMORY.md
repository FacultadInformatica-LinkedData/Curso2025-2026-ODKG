Hi!

For anyone working on **data cleansing with large datasets** (like myself), I recommend **increasing the maximum memory heap size** to at least **half of the available memory** on your machine.

---

## How to do it

1. Go to the folder where you installed **OpenRefine**.

2. Open the file **`openrefine.l4j.ini`** (or **`openrefine.l4j`**, depending on your OS).

3. Add or modify the following line: `-Xmx1024M`

4. Replace `1024` with the amount of memory (in MB) you want to assign. - A good rule of thumb is to use **half of your total RAM**. - For most cases, setting it to **4096M (4 GB)** should be more than enough.

---

After saving the file, restart **OpenRefine** for the changes to take effect.

It would be nice to put this message in a Markdown file in the `/HandsOn` directory so more people can see it
