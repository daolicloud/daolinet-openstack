#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>

#include <Python.h>

#define MAX_MSG_SIZE	32768

#define GENLMSG_DATA(glh)       ((void *)(NLMSG_DATA(glh) + GENL_HDRLEN))
#define NLA_DATA(na)            ((void *)((char *)(na) + NLA_HDRLEN))

enum {
	DOC_EXMPL_A_UNSPEC,
	DOC_EXMPL_A_MSG,
	__DOC_EXMPL_A_MAX,
};
#define DOC_EXMPL_A_MAX (__DOC_EXMPL_A_MAX - 1)

enum {
	DOC_EXMPL_C_UNSPEC,
	DOC_EXMPL_C_ECHO,
	__DOC_EXMPL_C_MAX,
};
#define DOC_EXMPL_C_MAX (__DOC_EXMPL_C_MAX - 1)

typedef struct msgtemplate {
	struct nlmsghdr n;
	struct genlmsghdr g;
	char data[MAX_MSG_SIZE];
} msgtemplate_t;


/**
 * * genl_send_msg - 通过generic netlink给内核发送数据
 * *
 * * @sd: 客户端socket
 * * @nlmsg_type: family_id
 * * @nlmsg_pid: 客户端pid
 * * @genl_cmd: 命令类型
 * * @genl_version: genl版本号
 * * @nla_type: netlink attr类型
 * * @nla_data: 发送的数据
 * * @nla_len: 发送数据长度
 * *
 * * return:
 * *    0:       成功
 * *    -1:      失败
 * */
int genl_send_msg(int sd, u_int16_t nlmsg_type, u_int32_t nlmsg_pid,
        u_int8_t genl_cmd, u_int8_t genl_version, u_int16_t nla_type,
        void *nla_data, int nla_len)
{
	struct nlattr *na;
	struct sockaddr_nl nladdr;
	int r, buflen;
	char *buf;
	msgtemplate_t msg;


	if (nlmsg_type == 0) {
		return 0;
	}

	msg.n.nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
	msg.n.nlmsg_type = nlmsg_type;
	msg.n.nlmsg_flags = NLM_F_REQUEST;
	msg.n.nlmsg_seq = 0;
	/*
	 * nlmsg_pid是发送进程的端口号。
	 * Linux内核不关心这个字段，仅用于跟踪消息。
	 */
	msg.n.nlmsg_pid = nlmsg_pid;
	msg.g.cmd = genl_cmd;
	msg.g.version = genl_version;
	na = (struct nlattr *) GENLMSG_DATA(&msg);
	na->nla_type = nla_type;
	na->nla_len = nla_len + 1 + NLA_HDRLEN;
	memcpy(NLA_DATA(na), nla_data, nla_len);
	msg.n.nlmsg_len += NLMSG_ALIGN(na->nla_len);

	buf = (char *) &msg;
	buflen = msg.n.nlmsg_len ;
	memset(&nladdr, 0, sizeof(nladdr));
	nladdr.nl_family = AF_NETLINK;
	while ((r = sendto(sd, buf, buflen, 0, (struct sockaddr *) &nladdr
				, sizeof(nladdr))) < buflen) {
		if (r > 0) {
			buf += r;
			buflen -= r;
		} else if (errno != EAGAIN) {
			return -1;
		}
	}
	return 0;
}


static int genl_get_family_id(int sd, char *family_name)
{
	msgtemplate_t ans;
	int id;
	struct nlattr *na;
	int rep_len;

	genl_send_msg(sd, GENL_ID_CTRL, 0, CTRL_CMD_GETFAMILY, 1,
			CTRL_ATTR_FAMILY_NAME, (void *)family_name,
			strlen(family_name)+1);

	rep_len = recv(sd, &ans, sizeof(ans), 0);
	if (rep_len < 0) {
		return 0;
	}
	if (ans.n.nlmsg_type == NLMSG_ERROR || !NLMSG_OK((&ans.n), rep_len)) {
		return 0;
	}

	na = (struct nlattr *) GENLMSG_DATA(&ans);
	na = (struct nlattr *) ((char *) na + NLA_ALIGN(na->nla_len));
	if (na->nla_type == CTRL_ATTR_FAMILY_ID) {
		id = *(__u16 *) NLA_DATA(na);
	} else {
		id = 0;
	}

	return id;
}


int genl_rcv_msg(int fid, int sock, void **data, size_t *len)
{
	int ret;
	struct msgtemplate msg;
	struct nlattr *na;

	ret = recv(sock, &msg, sizeof(msg), 0);
	if (ret < 0) {
		return -1;
	}

	if (msg.n.nlmsg_type == NLMSG_ERROR || !NLMSG_OK((&msg.n), ret)) {
		return -1;
	}

	if (msg.n.nlmsg_type == fid && fid != 0) {
		na = (struct nlattr *) GENLMSG_DATA(&msg);
		*data = (char *)NLA_DATA(na);
		*len = (size_t)na->nla_len - NLA_HDRLEN;
		return 0;
	}
	else
		return -1;
}


static int _py_genl_create(int *sock, int *family_id)
{
	int _sock = -1;
	int _family_id;
	struct sockaddr_nl local;

	// Create Generic Netlink Socket.
	errno = 0;
	_sock = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
	if (_sock < 0) {
		printf("Failed to create genl socket: %s", strerror(errno));
		goto error;
	}

	// Bind to the current pid.
	memset(&local, 0, sizeof(local));
	local.nl_family = AF_NETLINK;
	local.nl_pid = getpid();

	errno = 0;
	if (bind(_sock, (struct sockaddr *)&local, sizeof(local)) < 0) {
		printf("Failed to bind genl socket: %s", strerror(errno));
		goto error;
	}

	// Get family id
	_family_id = genl_get_family_id(_sock, "DOC_EXMPL");

	*sock = _sock;
	*family_id = _family_id;
	return 0;

error:
	if (_sock >= 0) {
		close(_sock);
	}
	return -1;
}


static int _py_genl_recv(int sock, int family_id, void **data, size_t *size)
{
	return genl_rcv_msg(family_id, sock, data, size);
}

static int _py_genl_send(int sock, int family_id, char *data, size_t size)
{
	return genl_send_msg(sock, family_id, getpid(), DOC_EXMPL_C_ECHO, 1,
			DOC_EXMPL_A_MSG, data, size);
}

////////////////////////////////////////////////////////

// create() ==> (sock, family_id)/None
static PyObject * py_genl_create(PyObject *self)
{
	int sock, family_id;

	if (_py_genl_create(&sock, &family_id) == -1) {
		Py_RETURN_NONE;
	}

	return Py_BuildValue("(ii)", sock, family_id);
}


// send(sock, family_id, data, size) ==> True(success)/False(failure)
static PyObject * py_genl_send(PyObject *self, PyObject *args)
{
	int sock;
	int family_id;
	char *data;
	unsigned long size;
	int _size;
	int ret;
	if (!PyArg_ParseTuple(args, "iiz#k", &sock, &family_id, &data, &_size, &size)) {
		return Py_BuildValue("i", -2);
		//return NULL;   // Raise a Exception
	}

	if (size != _size) {
		Py_RETURN_FALSE;
	}

	ret = _py_genl_send(sock, family_id, data, (size_t)size);
	if (!ret)
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}


// recv(sock, family_id)  ===> (byte_num, data)/None
static PyObject * py_genl_recv(PyObject *self, PyObject *args)
{
	int sock;
	int family_id;
	char *data;
	int err;
	size_t size;

	if (!PyArg_ParseTuple(args, "ii", &sock, &family_id)) {
		Py_RETURN_NONE;
	}

	err = _py_genl_recv(sock, family_id, (void*)&data, &size);
	if (err < 0) {
		Py_RETURN_NONE;
	}

	return Py_BuildValue("(Iz#)", size, data, size);
}


// close(sock) ==> None
static PyObject * py_genl_close(PyObject *self, PyObject *args)
{
	int sock;
	if (!PyArg_ParseTuple(args, "i", &sock)) {
		Py_RETURN_NONE;
	}

	if (sock >= 0)
		close(sock);

	Py_RETURN_NONE;
}

/////////////////
// send_skb(sock, family_id, data, size) ==> True(success)/False(failure)
static PyObject * py_genl_send_skb(PyObject *self, PyObject *args)
{
	return py_genl_send(self, args);
}

static PyMethodDef GENLMethods[] = {
	{"create", (PyCFunction)py_genl_create, METH_VARARGS, "Create a generic netlink socket"},
	{"send", (PyCFunction)py_genl_send, METH_VARARGS|METH_KEYWORDS, "Send a message to the kernle."},
	{"send_skb", (PyCFunction)py_genl_send_skb, METH_VARARGS|METH_KEYWORDS, "Send a message to the kernle."},
	{"recv", (PyCFunction)py_genl_recv, METH_VARARGS, "Receive a message from the kernle"},
	{"close", (PyCFunction)py_genl_close, METH_VARARGS, "Close the generic netlink socket"},
};

void initgenl(void)
{
	(void)Py_InitModule("genl", GENLMethods);
}

