FROM python:alpine3.7
COPY . /nodetree
WORKDIR /nodetree
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD [ "node.py", "run", "--host", "0.0.0.0"]