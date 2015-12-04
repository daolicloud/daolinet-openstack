#include "Python.h"
#include <unistd.h>
#include <fcntl.h>
#include <netinet/in.h>

struct hashkey {
    uint32_t odp_in_port;
    uint32_t in_port;
    uint32_t dp_ifindex;
    uint16_t dl_type;
    uint8_t dl_src[6];
    uint8_t dl_dst[6];
    uint8_t nw_proto;
    uint32_t nw_src;
    uint32_t nw_dst;
    uint16_t tp_src;
    uint16_t tp_dst;
    uint16_t icmp_identify;
    uint32_t packet_len;
    unsigned char packet[1600];
}__attribute__((packed));

static void __init_pipe(char *path)
{
    if (access(path, F_OK) == -1) {
        if (mkfifo(path, 0666) != 0) {
            fprintf(stderr, "create pipe failed: %s\n.", path);
        }
    }
}

PyObject *read_key(PyObject *self, PyObject *args)
{
    char *path;
    int pfd;
    char dl_src[18];
    char dl_dst[18];
    unsigned char packet[1600];
    uint8_t buff[sizeof(struct hashkey)+1];
    PyObject *pDict = PyDict_New();
    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;
    memset(buff, 0, sizeof(buff));
    memset(packet, 0, sizeof(packet));
    if ((pfd=open(path, O_RDONLY)) != -1) {
        if (read(pfd, buff, sizeof(struct hashkey)) > 0) {
            struct hashkey *hkey = (struct hashkey *)buff;
            PyDict_SetItemString(pDict, "odp_in_port",
                                 Py_BuildValue("I", hkey->odp_in_port));
            PyDict_SetItemString(pDict, "in_port",
                                 Py_BuildValue("I", hkey->in_port));
            PyDict_SetItemString(pDict, "dp_ifindex",
                                 Py_BuildValue("I", hkey->dp_ifindex));
            PyDict_SetItemString(pDict, "dl_type",
                                 Py_BuildValue("h", ntohs(hkey->dl_type)));
            snprintf(dl_src, 18, "%02x:%02x:%02x:%02x:%02x:%02x", hkey->dl_src[0],
                                                        hkey->dl_src[1],
                                                        hkey->dl_src[2],
                                                        hkey->dl_src[3],
                                                        hkey->dl_src[4],
                                                        hkey->dl_src[5]);
            PyDict_SetItemString(pDict, "dl_src", Py_BuildValue("s", dl_src));
            snprintf(dl_dst, 18, "%02x:%02x:%02x:%02x:%02x:%02x", hkey->dl_dst[0],
                                                        hkey->dl_dst[1],
                                                        hkey->dl_dst[2],
                                                        hkey->dl_dst[3],
                                                        hkey->dl_dst[4],
                                                        hkey->dl_dst[5]);
            PyDict_SetItemString(pDict, "dl_dst", Py_BuildValue("s", dl_dst));
            PyDict_SetItemString(pDict, "nw_proto",
                                 Py_BuildValue("b", hkey->nw_proto));
            PyDict_SetItemString(pDict, "nw_src",
                                 Py_BuildValue("I", ntohl(hkey->nw_src)));
            PyDict_SetItemString(pDict, "nw_dst",
                                 Py_BuildValue("I", ntohl(hkey->nw_dst)));
            PyDict_SetItemString(pDict, "tp_src", 
                                 Py_BuildValue("h", ntohs(hkey->tp_src)));
            PyDict_SetItemString(pDict, "tp_dst",
                                 Py_BuildValue("h", ntohs(hkey->tp_dst)));
            PyDict_SetItemString(pDict, "icmp_identify",
                                 Py_BuildValue("h", ntohs(hkey->icmp_identify)));
            PyDict_SetItemString(pDict, "packet_size",
                                 Py_BuildValue("I", hkey->packet_len));
            memcpy(packet, hkey->packet, hkey->packet_len);
            PyDict_SetItemString(pDict, "packet", Py_BuildValue("s#", packet, hkey->packet_len));
        }
        close(pfd);
    } else {
        fprintf(stderr, "open pipe failed: %s.\n", path);
    }
    return pDict;
}

PyObject *init_pipe(PyObject *self, PyObject *args)
{
    char *path;
    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;
    __init_pipe(path);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef keyMethods[] =
{
    {"init_pipe", init_pipe, METH_VARARGS, "init pipe and communicate with ovs later."},
    {"read_key", read_key, METH_VARARGS, "read key from pipe."},
    {NULL, NULL}
};

void initkeymod()
{
    Py_InitModule("keymod", keyMethods);
}
