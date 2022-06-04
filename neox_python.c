/* arm-linux-androideabi-gcc neox_python.c -o neox_python -ldl -pie
 * export LD_LIBRARY_PATH=./
 * cp libclient.so /path/to/neox_python
 */
#include <stdlib.h>
#include <memory.h>
#include <stdio.h>
#include <dlfcn.h>
#include <link.h>

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Usage: %s script.py\n", argv[0]);
        return 1;
    }

    FILE *fp = fopen(argv[1], "rb");
    fseek(fp, 0, SEEK_END);
    int file_len = ftell(fp);
    char *buf = (char *)malloc(file_len + 1);
    fseek(fp, 0, SEEK_SET);
    fread(buf, file_len, 1, fp);
    buf[file_len] = 0;

    void *lib = dlopen("libclient.so", RTLD_LAZY);
    if (!lib)
    {
        printf("Open Error:%s.\n", dlerror());
        return 0;
    }

    void *ACCESS_DESCRIPTION_free = dlsym(lib, "ACCESS_DESCRIPTION_free");
    void *base = ACCESS_DESCRIPTION_free - 0x016433CC;

    void (*Py_Initialize)();
    // Py_Initialize = dlsym(lib, "Py_Initialize"); // 未导出
    Py_Initialize = base + 0x0135ABA0 + 1;
    Py_Initialize();

    void (*PySys_SetArgv)(int, char **);
    PySys_SetArgv = base + 0x0136005C + 1;
    PySys_SetArgv(argc - 1, argv + 1);

    void (*PyRun_SimpleString)(char *);
    PyRun_SimpleString = base + 0x0135C796 + 1;
    PyRun_SimpleString(buf);

    void (*Py_Finalize)();
    Py_Finalize = base + 0x0135ABA8 + 1;
    Py_Finalize();

    dlclose(lib);
    free((void *)buf);
    return 0;
}