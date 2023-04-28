FROM postgres:13

ARG USERNAME=appuser
ENV APP_HOME=/home/$USERNAME \
	ACCEPT_EULA=Y \
    LANG=ru_RU.UTF-8 \
    LC_ALL=ru_RU.UTF-8
## set locale to datetime
RUN apt-get update && \
    apt-get install -y locales curl htop cron curl systemctl sudo && \
    which cron && rm -rf /etc/cron.*/* && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
#    # добавим редактор внутрь образа - для отладки
    curl https://getmic.ro | bash && \
    mv micro /usr/bin && \
	useradd --create-home $USERNAME && \
	usermod -aG sudo $USERNAME && \
	echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
	chmod 666 /etc/environment

USER $USERNAME

WORKDIR /usr/local/bin/
