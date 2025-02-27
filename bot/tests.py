from bot.handlers.helpers import (get_hashtype, get_ip, get_user,
                                  is_ip_address, text)


def test_get_hashtype():
    assert get_hashtype("anekobtw") is None
    assert get_hashtype("d54ac875cd839726552ca78c290bf728") == 0
    assert get_hashtype("9738908f98622497078779583ec10211") == 0
    assert get_hashtype("$SHA$b34a733a36443569$dd7063474737d80cad6bb3a016b7a1cd05f0416b9cbe3596f6542b4316549cf7") == 20711
    assert get_hashtype("$SHA$ed281aa0bf72a3b4$b8e000034f0fdd5c4ad113b45baede7c5d0801ed1b8c329b57b5d0d420c420bb") == 20711
    assert get_hashtype("$SHA$276ff1ec2be495e4$fea99922ef44a6454505a929603a0c41a68dd01aae300af02a5cd83197aac97c") == 20711
    assert get_hashtype("1231") is None


def test_is_ip_address():
    assert is_ip_address("135.229.227.183") == True
    assert is_ip_address("74.180.158.26") == True
    assert is_ip_address("52.237.56.51") == True
    assert is_ip_address("199.132.216.201") == True
    assert is_ip_address("anekobtw") == False
    assert is_ip_address("1289379") == False
    assert is_ip_address("199132216201") == False
    assert is_ip_address("192.168.1.1") is True
    assert is_ip_address("10.0.0.1") is True
    assert is_ip_address("256.256.256.256") is False
    assert is_ip_address("not_an_ip") is False
    assert is_ip_address("0.0.0.0") is True
    assert is_ip_address("255.255.255.255") is True
    assert is_ip_address("999.999.999.999") is False


def test_text():
    assert text("welcome") == "👋 Откройте мир возможностей с нами! Мы собираем данные из открытых источников, соблюдая законность их получения, и преобразуем их в полезную информацию, необходимую для поиска.\n\n<b>Выберите нужное действие:</b>"


def test_get_user():
    assert get_user("anekobtw") == {"username": {}, "hash": {}, "ip": {}, "password": {}, "server": {}}
    assert type(get_user("Login221")) == dict
    assert get_user("Login221")["hash"][0] == "$SHA$b34a733a36443569$dd7063474737d80cad6bb3a016b7a1cd05f0416b9cbe3596f6542b4316549cf7"


def test_get_ip():
    assert get_ip("1237192837981273987") == {"username": {}, "hash": {}, "ip": {}, "password": {}, "server": {}}
    assert list(get_ip("190.175.44.27")["username"].values())[0] == "scorpion119"
    assert list(get_ip("201.105.184.57")["server"].values())[0] == "BorkLand"
    assert list(get_ip("127.0.0.1")["hash"].values())[0] == "$SHA$d318d7096a032db0$f839f4d5c046354b585a43f3aa34c8de504c9712bb5eb304fc8ac54c7a6e4824"
